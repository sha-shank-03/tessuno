"""Extracted-kit workflow checks; no host, model, compiler or publication qualification."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build as builder
from library import ROOT, CONTROLS, Invalid, load_catalog


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links = []; self.ids = set(); self.tags = []; self.lang = ''; self.policy = ''
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs); self.tags.append(tag)
        if tag in ('a', 'link'): self.links.append(attrs['href'])
        if 'id' in attrs: self.ids.add(attrs['id'])
        if tag == 'html': self.lang = attrs.get('lang')
        if tag == 'meta' and attrs.get('http-equiv') == 'Content-Security-Policy':
            self.policy = attrs['content']


class SourceWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        builder.build()
        cls.archive = ROOT / 'dist/prototype.zip'

    def run_tool(self, root, *args, expected=0):
        result = subprocess.run([sys.executable, '-B', *args], cwd=root,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def copy_root(self, parent):
        root = parent / 'candidate'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__'))
        return root

    def build_at(self, root):
        with patch.object(builder, 'ROOT', root), patch.object(builder, 'load_catalog', lambda: load_catalog(root)):
            return builder.build()

    def test_inventory_preserves_every_archive_byte_and_object_closure(self):
        with zipfile.ZipFile(self.archive) as archive:
            names = archive.namelist()
            self.assertEqual(names, sorted(set(names)))
            inventory = json.loads(archive.read('inspection-kit.json'))
            self.assertEqual(inventory['status'], 'source-only')
            for flag in ('runtimeQualified', 'trustedEvidence', 'installationPerformed'):
                self.assertIs(inventory[flag], False)
            hashes = {entry['path']: entry['sha256'] for entry in inventory['files']}
            self.assertEqual(len(hashes), len(inventory['files']))
            self.assertEqual(set(hashes), set(names) - {'inspection-kit.json'})
            for name in names:
                self.assertFalse(Path(name).is_absolute())
                self.assertNotIn('..', Path(name).parts)
                info = archive.getinfo(name)
                self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(info.external_attr >> 16, 0o100644)
                if name in hashes:
                    self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), hashes[name])
            manifests = json.loads(archive.read('content-manifests.json'))
            self.assertEqual(len(manifests), 10)
            for bundle in manifests.values():
                for entry in bundle['manifest']['files']:
                    data = archive.read(entry['path'])
                    self.assertEqual(data, (ROOT / entry['path']).read_bytes())
                    self.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'])
            self.assertEqual(archive.read('README.md'), (ROOT / 'docs/source-workflow.md').read_bytes())
            self.assertEqual(archive.read('requirements-dev.lock'), (ROOT / 'requirements-dev.lock').read_bytes())
        first = self.archive.read_bytes()
        builder.build()
        self.assertEqual(first, self.archive.read_bytes())

    def test_documented_commands_work_after_fresh_extraction(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with zipfile.ZipFile(self.archive) as archive: archive.extractall(root)
            validation = self.run_tool(root, 'tools/validate.py')
            self.assertIn('PASS: 10 objects', validation.stdout)
            diagnosis = json.loads(self.run_tool(root, 'tools/evaluate_build_diagnosis.py', '--examples').stdout)
            self.assertEqual(len(diagnosis), 5)
            self.assertEqual(sum(row['assertionsPassed'] for row in diagnosis), 35)
            for row in diagnosis:
                self.assertEqual(row['status'], 'pass')
                self.assertIs(row['modelInvokedByScorer'], False)
                self.assertIs(row['xcodeInvokedByScorer'], False)
            packet = json.loads(self.run_tool(root, 'tools/evaluate_release_packet.py',
                    'skills/release-readiness-evidence/fixtures/complete.json').stdout)
            self.assertEqual(packet['inventoryStatus'], 'complete')
            self.assertEqual(packet['releaseVerdict'], 'BLOCKED')
            for flag in ('trustedEvidence', 'runtimeInvoked', 'modelInvoked'):
                self.assertIs(packet[flag], False)
            skill = json.loads(self.run_tool(root, 'tools/inspect_skill_portability.py',
                                            '--skill', 'core/ios-test-plan').stdout)
            agent = json.loads(self.run_tool(root, 'tools/export_adapter.py',
                                            '--agent', 'core/ios-quality-reviewer').stdout)
            for report in (skill, agent):
                self.assertIs(report['runtimeQualified'], False)
                self.assertIs(report['executableExportAllowed'], False)
                self.assertIs(report['generator']['authenticated'], False)
                for entry in report['generator']['files']:
                    self.assertEqual(hashlib.sha256((root / entry['path']).read_bytes()).hexdigest(), entry['sha256'])
            self.assertEqual(len(skill['hosts']), 4)
            for host in skill['hosts']:
                self.assertIsNone(host['version'])
                self.assertEqual(host['versionStatus'], 'unobserved')
                self.assertEqual(host['unsupportedControls'], list(CONTROLS))
            self.assertIsNone(agent['host']['version'])
            self.assertEqual(agent['adapter']['unsupported'], list(CONTROLS))

    def test_extracted_kit_rejects_execution_publication_and_invalid_sidecar(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with zipfile.ZipFile(self.archive) as archive: archive.extractall(root)
            for tool, flag, id in (('tools/inspect_skill_portability.py', '--skill', 'core/ios-test-plan'),
                                   ('tools/export_adapter.py', '--agent', 'core/ios-quality-reviewer')):
                result = self.run_tool(root, tool, flag, id, '--executable', expected=1)
                self.assertEqual(result.stdout, '')
                self.assertIn('executable export rejected', result.stderr)
                for control in CONTROLS: self.assertIn(control, result.stderr)
            publication = self.run_tool(root, 'tools/validate.py', '--publication', expected=1)
            self.assertEqual(publication.stdout, '')
            self.assertIn('FAIL:', publication.stderr)
            sidecar = root / 'skills/ios-test-plan/library.json'
            item = json.loads(sidecar.read_text()); item['unknownAuthority'] = True
            sidecar.write_text(json.dumps(item))
            self.assertIn('FAIL:', self.run_tool(root, 'tools/validate.py', expected=1).stderr)

    def test_support_allowlist_excludes_checkout_and_runner_content(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.copy_root(Path(folder))
            for name in ('tools/private-note.py', 'docs/private-note.md', '.agents/private-note.md'):
                path = root / name; path.parent.mkdir(exist_ok=True); path.write_text('must not ship\n')
            self.build_at(root)
            with zipfile.ZipFile(root / 'dist/prototype.zip') as archive:
                names = set(archive.namelist())
                expected_tools = {'tools/library.py', 'tools/validate.py', 'tools/evaluate_build_diagnosis.py',
                                  'tools/evaluate_release_packet.py', 'tools/export_adapter.py',
                                  'tools/inspect_skill_portability.py', 'tools/skill-host-profiles.json'}
                self.assertEqual({name for name in names if name.startswith('tools/')}, expected_tools)
                self.assertEqual({name for name in names if name.startswith('docs/')},
                                 {'docs/source-workflow.md', 'docs/release-checklist.md'})
                for prefix in ('.git/', '.github/', '.agents/', 'tests/', 'fixtures/'):
                    self.assertFalse(any(name.startswith(prefix) for name in names))

    def test_missing_and_symlinked_support_reject_before_output_creation(self):
        sources = set(builder.KIT_SUPPORT.values()) | {
            'site/source-workflow.html', 'evals/xcode-build-diagnosis/cases/mixed-diagnostics.json'}
        for source in sorted(sources):
            for mode in ('missing', 'symlink'):
                with self.subTest(source=source, mode=mode), tempfile.TemporaryDirectory() as folder:
                    root = self.copy_root(Path(folder)); path = root / source
                    path.unlink()
                    if mode == 'symlink': path.symlink_to(ROOT / source)
                    with self.assertRaises(Invalid): self.build_at(root)
                    self.assertFalse((root / 'dist').exists())

    def test_start_page_links_resolve_to_exact_sources_and_object_fragments(self):
        dist = ROOT / 'dist'; workflow = Page((dist / 'source-workflow.html').read_text())
        self.assertEqual(workflow.lang, 'en')
        self.assertNotIn('script', workflow.tags)
        self.assertEqual(workflow.policy, "default-src 'none'; style-src 'self'; base-uri 'none'; form-action 'none'")
        for link in workflow.links:
            parsed = urlsplit(link)
            self.assertEqual(parsed.scheme, '')
            target = dist / unquote(parsed.path)
            self.assertTrue(target.is_file(), link)
            if parsed.fragment: self.assertIn(unquote(parsed.fragment), Page(target.read_text()).ids)
        catalog = Page((dist / 'index.html').read_text())
        self.assertIn('source-workflow.html', catalog.links)
        self.assertIn('prototype.zip', catalog.links)
        for name in ('source-workflow', 'release-checklist'):
            self.assertEqual((dist / ('source/docs/' + name + '.md.txt')).read_bytes(),
                             (ROOT / ('docs/' + name + '.md')).read_bytes())


if __name__ == '__main__': unittest.main()
