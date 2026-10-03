"""Declared scope summaries and alternate-root validation; no host enforcement."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build as builder
import library
from export_adapter import inspect_adapter
from inspect_skill_portability import inspect_skill
from library import ROOT, Invalid, canonical, load_catalog, read_json


class Cards(HTMLParser):
    def __init__(self):
        super().__init__(); self.cards = {}; self.current = None

    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            attrs = dict(attrs); self.current = attrs['data-search'].split()[0]
            self.cards[self.current] = {'search': attrs['data-search'], 'text': ''}

    def handle_data(self, data):
        if self.current is not None: self.cards[self.current]['text'] += data

    def handle_endtag(self, tag):
        if tag == 'article': self.current = None


class CatalogScopes(unittest.TestCase):
    def copy_catalog(self, parent, name):
        root = parent / name
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__', 'scratch'))
        return root

    def writable_skill(self, root):
        path = root / 'skills/ios-test-plan/library.json'; record = read_json(path)
        record['filesystemScope']['write'] = ['${workspace}/outputs/**']
        path.write_bytes(canonical(record))
        return record

    def test_nested_dependency_controls_index_page_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as d:
            root = self.copy_catalog(Path(d), 'candidate'); skill = self.writable_skill(root)
            skill['networkScope'] = {'mode': 'allowlist', 'destinations': ['example.invalid'], 'externalWriteAllowed': False}
            (root / 'skills/ios-test-plan/library.json').write_bytes(canonical(skill))
            # Force Pack -> Recipe -> Agent -> Skill; no direct Skill reference shortcuts.
            path = root / 'recipes/ios-change-review/recipe.json'; recipe = read_json(path)
            recipe['steps'] = [recipe['steps'][1]]; path.write_bytes(canonical(recipe))
            path = root / 'packs/ios-studio/pack.json'; pack = read_json(path)
            pack['members'] = [pack['members'][2]]; path.write_bytes(canonical(pack))
            records = load_catalog(root)
            with patch.object(builder, 'ROOT', root), patch.object(builder, 'load_catalog', lambda: load_catalog(root)):
                first = builder.build(); self.assertEqual(first, builder.build())
            for name, sha in first.items():
                self.assertEqual(hashlib.sha256((root / 'dist' / name).read_bytes()).hexdigest(), sha)
            index = {item['id']: item for item in read_json(root / 'dist/search-index.json')}
            page = Cards(); page.feed((root / 'dist/index.html').read_text())
            for key in ['core/ios-test-plan', 'core/ios-quality-reviewer', 'core/ios-change-review', 'core/ios-studio']:
                with self.subTest(object=key):
                    self.assertEqual(index[key]['write'], 'declared')
                    self.assertEqual(index[key]['network'], 'allowlist')
                    controls = index[key]['declaredControls']
                    self.assertEqual(controls['basis'], 'exact-dependency-closure')
                    self.assertEqual(controls['enforcementStatus'], 'unqualified')
                    self.assertEqual([item['id'] for item in controls['components']], library.closure(records, key))
                    declared = {item['id']: item['declaredPermissions'] for item in controls['components']}
                    self.assertEqual(declared['core/ios-test-plan']['filesystemScope'], skill['filesystemScope'])
                    self.assertEqual(declared['core/ios-test-plan']['networkScope'], skill['networkScope'])
                    self.assertIn('write:declared', page.cards[key]['search'])
                    self.assertNotIn('write:none', page.cards[key]['search'])
                    self.assertIn('network:allowlist', page.cards[key]['search'])
                    self.assertIn('network: allowlist; write: declared', page.cards[key]['text'])
                    self.assertIn('no enforcement or combined permission policy', page.cards[key]['text'])
                    self.assertIn('example.invalid', page.cards[key]['text'])

    def test_current_read_only_closure_summary(self):
        builder.build()
        for item in read_json(ROOT / 'dist/search-index.json'):
            with self.subTest(object=item['id']):
                self.assertEqual(item['write'], 'none'); self.assertEqual(item['network'], 'none')
                self.assertEqual(item['declaredControls']['enforcementStatus'], 'unqualified')

    def test_candidate_scope_symlink_rejected_with_clean_tool_root(self):
        with tempfile.TemporaryDirectory() as d:
            parent = Path(d); candidate = self.copy_catalog(parent, 'candidate')
            tool = self.copy_catalog(parent, 'tool'); self.writable_skill(candidate)
            outside = parent / 'synthetic-outside'; outside.mkdir()
            (candidate / 'outputs').symlink_to(outside, target_is_directory=True)
            with patch.object(library, 'ROOT', tool):
                for inspect in [lambda: load_catalog(candidate),
                                lambda: inspect_adapter('core/ios-quality-reviewer', root=candidate),
                                lambda: inspect_skill('core/ios-test-plan', root=candidate)]:
                    with self.subTest(consumer=inspect), self.assertRaisesRegex(Invalid, 'symlink forbidden: outputs/\\*\\*'):
                        inspect()

    def test_clean_candidate_accepted_with_unrelated_tool_scope_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            parent = Path(d); candidate = self.copy_catalog(parent, 'candidate')
            tool = self.copy_catalog(parent, 'tool'); self.writable_skill(candidate)
            outside = parent / 'synthetic-outside'; outside.mkdir()
            (tool / 'inputs').symlink_to(outside, target_is_directory=True)
            expected = load_catalog(candidate)
            with patch.object(library, 'ROOT', tool):
                self.assertEqual(load_catalog(candidate), expected)
                for report in [inspect_adapter('core/ios-quality-reviewer', root=candidate),
                               inspect_skill('core/ios-test-plan', root=candidate)]:
                    self.assertFalse(report['runtimeQualified']); self.assertFalse(report['executableExportAllowed'])


if __name__ == '__main__':
    unittest.main()
