from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from check_ci_proposal import ROOT, check
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
        self.assertFalse(list((ROOT / '.github/workflows').glob('*')))

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
