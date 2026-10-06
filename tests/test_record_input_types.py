"""Malformed JSON records reject through the domain error used by offline callers."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from library import ROOT, Invalid, load_catalog, validate_schema
import build as builder

NON_OBJECTS = (None, False, True, 0, 1.5, '', 'Agent', [], ['Agent'])
BAD_KINDS = (None, False, True, 0, 1.5, [], {}, ['Skill'])


class RecordInputTypes(unittest.TestCase):
    def cli(self, root, flags=(), expected=1):
        result = subprocess.run([sys.executable, '-B', 'tools/validate.py', *flags], cwd=root,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, expected, result.stderr)
        if expected == 1:
            self.assertEqual(result.stdout, '')
            self.assertTrue(result.stderr.startswith('FAIL: '), result.stderr)
            self.assertNotIn('Traceback', result.stderr)
        return result

    def test_non_objects_raise_domain_errors_with_inferred_or_explicit_schema(self):
        for schema in (None, 'agent', 'skill', 'recipe', 'pack', 'evidence'):
            for value in NON_OBJECTS:
                with self.subTest(schema=schema, value=value), self.assertRaisesRegex(Invalid, 'JSON object'):
                    validate_schema(value, schema)

    def test_non_string_kinds_reject_without_dispatch_exception(self):
        agent = load_catalog()['core/ios-quality-reviewer']['record']
        for value in BAD_KINDS:
            record = copy.deepcopy(agent); record['kind'] = value
            with self.subTest(value=value), self.assertRaisesRegex(Invalid, 'kind must be a string'):
                validate_schema(record)
            with self.subTest(explicit=True, value=value), self.assertRaises(Invalid):
                validate_schema(record, 'agent')

    def test_all_catalog_kinds_and_cli_modes_reject_malformed_json_records(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve() / 'candidate'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__'))
            records = load_catalog(root)
            for kind in ('Agent', 'Skill', 'Recipe', 'Pack'):
                info = next(info for info in records.values() if info['record']['kind'] == kind)
                path = info['path']; original = path.read_bytes()
                cases = [(value, 'JSON object') for value in NON_OBJECTS]
                for value in BAD_KINDS:
                    record = copy.deepcopy(info['record']); record['kind'] = value
                    cases.append((record, 'kind must be a string'))
                for record, error in cases:
                    with self.subTest(kind=kind, record=record):
                        path.write_text(json.dumps(record))
                        with self.assertRaisesRegex(Invalid, error): load_catalog(root)
                for record in (None, {**info['record'], 'kind': []}):
                    path.write_text(json.dumps(record))
                    for flags in ((), ('--project-policy',), ('--publication',), ('--project-policy', '--publication')):
                        with self.subTest(kind=kind, flags=flags, record=record): self.cli(root, flags)
                path.write_bytes(original)
            self.assertEqual(set(load_catalog(root)), set(records))

    def test_valid_records_and_default_cli_output_stay_compatible(self):
        records = load_catalog()
        self.assertEqual(len(records), 10)
        for info in records.values():
            validate_schema(info['record'])
            validate_schema(info['record'], info['record']['kind'].lower())
        default = self.cli(ROOT, expected=0)
        self.assertEqual(default.stdout, 'PASS: 10 objects; schema, native skill, scopes, references and paths checked. Compatibility remains declared-only.\n')
        self.assertEqual(default.stderr, '')
        for record in ({}, {'kind': 'unknown'}, {'kind': ''}):
            with self.subTest(record=record), self.assertRaisesRegex(Invalid, 'unknown record kind'):
                validate_schema(record)

    def test_extracted_kit_rejects_bad_manifest_through_clean_fail_output(self):
        builder.build()
        with tempfile.TemporaryDirectory() as folder, zipfile.ZipFile(ROOT / 'dist/prototype.zip') as archive:
            root = Path(folder).resolve(); archive.extractall(root)
            self.cli(root, expected=0)
            self.cli(root, ('--project-policy',), expected=0)
            path = root / 'agents/ios-quality-reviewer/agent.json'
            path.write_text('null\n')
            for flags in ((), ('--project-policy',), ('--publication',), ('--project-policy', '--publication')):
                result = self.cli(root, flags)
                self.assertEqual(result.stderr, 'FAIL: record must be a JSON object\n')


if __name__ == '__main__': unittest.main()
