"""Original-project declaration checks, separate from generic schemas and release authority."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from library import ROOT, Invalid, load_catalog, project_identity_check, subject_manifest, validate_schema
import build as builder


class ProjectIdentity(unittest.TestCase):
    def copy_root(self, parent):
        root = parent / 'candidate'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__'))
        return root

    def cli(self, root, *flags, expected=0):
        result = subprocess.run([sys.executable, '-B', 'tools/validate.py', *flags], cwd=root,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, expected, result.stderr)
        return result

    def test_selected_declarations_pass_without_changing_ids_or_versions(self):
        records = load_catalog()
        self.assertEqual(len(records), 10)
        self.assertTrue(project_identity_check(records))
        for id, info in records.items():
            self.assertEqual(info['record']['id'], id)
            self.assertEqual(info['record']['version'], '0.1.0')
            self.assertEqual(info['record']['maintainer'],
                             {'name': 'sha-shank-03', 'contact': 'https://github.com/sha-shank-03'})
        default = self.cli(ROOT)
        self.assertEqual(default.stdout, 'PASS: 10 objects; schema, native skill, scopes, references and paths checked. Compatibility remains declared-only.\n')
        selected = self.cli(ROOT, '--project-policy')
        self.assertTrue(selected.stdout.startswith(default.stdout))
        self.assertIn('Identity authentication and comprehensive license validation remain unavailable', selected.stdout)

    def test_generic_catalog_accepts_other_declarations_but_project_check_rejects(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.copy_root(Path(folder))
            original = load_catalog(root)
            for kind in ('Agent', 'Skill', 'Recipe', 'Pack'):
                info = next(info for info in original.values() if info['record']['kind'] == kind)
                path = info['path']; before = path.read_bytes()
                for field, value in (
                    ('license', 'MIT'), ('license', 'Apache-2.0 OR MIT'), ('license', 'UNDECIDED'),
                    ('maintainer', {'name': 'Other declared maintainer', 'contact': 'unverified-contact'}),
                    ('maintainer', {'name': 'sha-shank-03', 'contact': 'https://example.invalid'}),
                ):
                    with self.subTest(kind=kind, field=field, value=value):
                        item = copy.deepcopy(info['record']); item[field] = value
                        validate_schema(item, root=root)
                        path.write_text(json.dumps(item))
                        records = load_catalog(root)
                        with self.assertRaisesRegex(Invalid, 'project policy:'): project_identity_check(records, root)
                        path.write_bytes(before)
            path = root / 'skills/ios-test-plan/library.json'
            item = json.loads(path.read_text()); item['license'] = 'MIT'
            path.write_text(json.dumps(item))
            self.cli(root)
            rejected = self.cli(root, '--project-policy', expected=1)
            self.assertEqual(rejected.stdout, '')
            self.assertIn('core/ios-test-plan license declaration must be Apache-2.0', rejected.stderr)

    def test_changed_missing_and_symlinked_license_reject(self):
        for mode in ('changed', 'missing', 'symlink'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                root = self.copy_root(Path(folder)); license = root / 'LICENSE'
                if mode == 'changed':
                    license.write_bytes(license.read_bytes() + b'\n')
                    records = load_catalog(root)  # Generic source syntax does not select license policy.
                    with self.assertRaisesRegex(Invalid, 'approved Apache-2.0 text'):
                        project_identity_check(records, root)
                else:
                    license.unlink()
                    if mode == 'symlink': license.symlink_to(ROOT / 'LICENSE')
                result = self.cli(root, '--project-policy', expected=1)
                self.assertEqual(result.stdout, '')
                self.assertIn('FAIL:', result.stderr)

    def test_project_pass_keeps_publication_blocked_and_schema_errors_closed(self):
        for flags in (('--publication',), ('--project-policy', '--publication')):
            result = self.cli(ROOT, *flags, expected=1)
            self.assertEqual(result.stdout, '')
            self.assertIn('publication blocked', result.stderr)
        with tempfile.TemporaryDirectory() as folder:
            root = self.copy_root(Path(folder)); path = root / 'skills/ios-test-plan/library.json'
            item = json.loads(path.read_text()); item['maintainer']['authenticated'] = True
            path.write_text(json.dumps(item))
            for flags in ((), ('--project-policy',)):
                result = self.cli(root, *flags, expected=1)
                self.assertEqual(result.stdout, '')
                self.assertIn('Additional properties are not allowed', result.stderr)
        with self.assertRaisesRegex(Invalid, 'empty catalog'): project_identity_check({})

    def test_metadata_changes_invalidate_content_without_rewriting_native_skill(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.copy_root(Path(folder)); records = load_catalog(root)
            subject = subject_manifest(root, records, 'core/ios-studio')[0]
            native = root / 'skills/ios-test-plan/SKILL.md'; original = native.read_bytes()
            sidecar = root / 'skills/ios-test-plan/library.json'
            item = json.loads(sidecar.read_text()); item['maintainer']['contact'] = 'UNDECIDED'
            sidecar.write_text(json.dumps(item))
            changed = subject_manifest(root, load_catalog(root), 'core/ios-studio')[0]
            self.assertNotEqual(subject['sha256'], changed['sha256'])
            self.assertEqual(subject['id'], changed['id'])
            self.assertEqual(subject['version'], changed['version'])
            self.assertEqual(native.read_bytes(), original)

    def test_opt_in_command_and_exact_metadata_work_in_extracted_kit(self):
        builder.build()
        with tempfile.TemporaryDirectory() as folder, zipfile.ZipFile(ROOT / 'dist/prototype.zip') as archive:
            root = Path(folder).resolve(); archive.extractall(root)
            self.cli(root)
            result = self.cli(root, '--project-policy')
            self.assertIn('original-project maintainer/license declarations', result.stdout)
            self.cli(root, '--project-policy', '--publication', expected=1)
            inventory = json.loads(archive.read('inspection-kit.json'))
            hashes = {entry['path']: entry['sha256'] for entry in inventory['files']}
            for info in load_catalog(root).values():
                path = info['path'].relative_to(root).as_posix()
                self.assertEqual(archive.read(path), (ROOT / path).read_bytes())
                self.assertEqual(hashlib.sha256(archive.read(path)).hexdigest(), hashes[path])
            self.assertIn('python -B tools/validate.py --project-policy', archive.read('README.md').decode())


if __name__ == '__main__': unittest.main()
