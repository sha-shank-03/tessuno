from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from check_ci_proposal import ROOT, CONTROLLER, check, check_live_workflows
from check_source_format import check as format_check
from ci_checks import COMMANDS


class CIProposal(unittest.TestCase):
    def text(self):
        return (ROOT / 'docs/ci/validation.yml.disabled').read_text()

    def test_inert_pinned_proposal_and_command_parity(self):
        data = check(self.text())
        self.assertEqual(data['jobs']['inspect']['if'], '${{ false }}')
        self.assertEqual(COMMANDS, (('tools/check_source_format.py',), ('tools/validate.py',),
                                   ('-m', 'unittest', 'discover', '-s', 'tests', '-v'), ('tools/build.py',)))
        self.assertEqual(check_live_workflows(), 1)

    def test_exact_reviewed_controller_admission(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            self.assertEqual(check_live_workflows(root), 0)
            directory = root / '.github/workflows'
            directory.mkdir(parents=True)
            self.assertEqual(check_live_workflows(root), 0)
            (directory / CONTROLLER).write_bytes((ROOT / '.github/workflows' / CONTROLLER).read_bytes())
            self.assertEqual(check_live_workflows(root), 1)

    def test_controller_changes_and_extra_workflows_reject(self):
        original = (ROOT / '.github/workflows' / CONTROLLER).read_bytes()
        changes = [(b'contents: read', b'contents: write'),
                   (b'workflow_dispatch:', b'pull_request:'),
                   (b'ade193beda810f85ac38fa008f25f7261c272b23', b'main'),
                   (b'3d3c42e5aac5ba805825da76410c181273ba90b1', b'v7')]
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent); directory = root / '.github/workflows'
            directory.mkdir(parents=True); controller = directory / CONTROLLER
            for old, new in changes:
                self.assertIn(old, original)
                controller.write_bytes(original.replace(old, new))
                with self.subTest(change=old), self.assertRaisesRegex(ValueError, 'bytes changed'):
                    check_live_workflows(root)
            controller.write_bytes(original + b'# unreviewed change\n')
            with self.assertRaisesRegex(ValueError, 'bytes changed'):
                check_live_workflows(root)
            controller.write_bytes(original)
            (directory / 'unreviewed.yml').write_text('on: push\njobs: {}\n')
            with self.assertRaisesRegex(ValueError, 'unreviewed workflow path'):
                check_live_workflows(root)

    def test_workflow_symlinks_and_unexpected_paths_reject_before_reading(self):
        for location in ('.github', '.github/workflows', '.github/workflows/' + CONTROLLER):
            with self.subTest(location=location), tempfile.TemporaryDirectory() as parent:
                root = Path(parent) / 'repo'; root.mkdir()
                outside = Path(parent) / 'outside'
                if location.endswith(CONTROLLER): outside.write_text('must not be read')
                else: outside.mkdir()
                target = root / location; target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(outside, target_is_directory=outside.is_dir())
                with patch.object(Path, 'read_bytes', side_effect=AssertionError('must reject before reading')):
                    with self.assertRaises(ValueError): check_live_workflows(root)
        for name in ('other.yml', CONTROLLER):
            with self.subTest(directory=name), tempfile.TemporaryDirectory() as parent:
                root = Path(parent); (root / '.github/workflows' / name).mkdir(parents=True)
                with patch.object(Path, 'read_bytes', side_effect=AssertionError('must reject before reading')):
                    with self.assertRaises(ValueError): check_live_workflows(root)

    def test_mutations_cannot_silently_relax_plan(self):
        changes = [('pull_request:', 'pull_request_target:'), ('permissions: {}', 'permissions: write-all'),
                   ('contents: read', 'contents: write'), ('${{ false }}', '${{ true }}'),
                   ('persist-credentials: false', 'persist-credentials: true'), ('exit 1', 'exit 0'),
                   ('--no-index ', ''), ('--require-hashes ', ''),
                   ('11bd71901bbe5b1630ceea73d27597364c9af683', 'v4'),
                   ('timeout-minutes: 10', 'timeout-minutes: 60')]
        for old, new in changes:
            with self.subTest(change=old), self.assertRaises(ValueError):
                check(self.text().replace(old, new))
        with self.assertRaises(ValueError):
            check(self.text() + '\npermissions: {}\n')

    def test_hygiene_negative_and_positive(self):
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent)
            (root / 'tools').mkdir()
            path = root / 'tools/original.py'
            path.write_text('value = 1\n')
            self.assertEqual(format_check(root), 1)
            for text in ['value = 1 \n', 'value = 1', 'value = (\n']:
                path.write_text(text)
                with self.assertRaises((ValueError, SyntaxError)):
                    format_check(root)

    def test_acquisition_and_hard_stop_guards(self):
        changes = [
            ('ref: f19a87ab6d1a390f0c1848b2338b21301163494e',
             'ref: refs/pull/${{ github.event.pull_request.number }}/merge'),
            ('ref: refs/pull/${{ github.event.pull_request.number }}/merge', 'ref: main'),
            ('path: protected', 'path: candidate'),
            ('path: candidate', 'path: protected'),
            ('runs-on: ubuntu-24.04', 'runs-on: ubuntu-latest'),
            ('      - name: Stop until independently reviewed isolation exists',
             '      - continue-on-error: true\n        name: Stop until independently reviewed isolation exists'),
            ('      - name: Offline dependencies from protected lock (prospective only)',
             '      - if: ${{ always() }}\n        name: Offline dependencies from protected lock (prospective only)'),
            ('      - name: Candidate command parity (untrusted; prospective only)',
             '      - if: ${{ always() }}\n        name: Candidate command parity (untrusted; prospective only)'),
        ]
        for old, new in changes:
            with self.subTest(change=old), self.assertRaises(ValueError):
                check(self.text().replace(old, new))

    def test_scanned_directory_symlinks_reject_before_reading(self):
        from unittest.mock import patch
        for folder in ('tools', 'tests', 'schemas', 'site', 'site/assets', 'tools/nested'):
            with self.subTest(folder=folder), tempfile.TemporaryDirectory() as parent:
                root = Path(parent) / 'repo'
                root.mkdir()
                outside = Path(parent) / 'outside'
                outside.mkdir()
                (outside / 'original.py').write_text('value = 1\n')
                target = root / folder
                target.parent.mkdir(parents=True, exist_ok=True)
                target.symlink_to(outside, target_is_directory=True)
                with patch.object(Path, 'read_bytes', side_effect=AssertionError('must reject before reading outside source')):
                    with self.assertRaises(ValueError):
                        format_check(root)
        with tempfile.TemporaryDirectory() as parent:
            root = Path(parent) / 'repo'
            (root / 'tools').mkdir(parents=True)
            (root / 'tools/original.py').write_text('value = 1\n')
            alias = Path(parent) / 'repo-alias'
            alias.symlink_to(root, target_is_directory=True)
            self.assertEqual(format_check(alias), format_check(root))
