import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from evaluate_release_packet import DOMAINS, FIXTURES, evaluate
from library import ROOT, Invalid, canonical, trust_evidence


class ReleasePacket(unittest.TestCase):
    def fixture(self, parent):
        root = Path(parent) / 'repo'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__'))
        return root

    def packet(self, name='complete'):
        return json.loads((ROOT / f'{FIXTURES}{name}.json').read_text())

    def run_packet(self, root, packet):
        path = root / f'{FIXTURES}case.json'
        path.write_bytes(canonical(packet))
        return evaluate(path.relative_to(root).as_posix(), root=root)

    def row(self, result, domain):
        return next(row for row in result['domains'] if row['domain'] == domain)

    def test_complete_inventory_still_blocks_release_and_trust(self):
        result = evaluate(FIXTURES + 'complete.json')
        self.assertEqual(result, evaluate(FIXTURES + 'complete.json'))
        self.assertEqual(result['inventoryStatus'], 'complete')
        self.assertEqual(result['releaseVerdict'], 'BLOCKED')
        self.assertFalse(result['runtimeInvoked']); self.assertFalse(result['modelInvoked']); self.assertFalse(result['trustedEvidence'])
        self.assertEqual([row['domain'] for row in result['domains']], list(DOMAINS))
        with self.assertRaises(Invalid):
            trust_evidence(json.loads((ROOT / f'{FIXTURES}artifacts/tests.json').read_text()))

    def test_authored_missing_stale_mismatch_failure_and_not_run_cases(self):
        cases = [('missing','metadata-privacy','missing-domain'), ('stale','tests','stale-or-future-observation'),
                 ('mismatched','tests','version-build-mismatch'), ('mismatched','review','candidate-scope-mismatch'),
                 ('failure-and-not-run','tests','not-run'), ('failure-and-not-run','crashes','reported-fail')]
        for case, domain, code in cases:
            with self.subTest(case=case, domain=domain):
                result = evaluate(FIXTURES + case + '.json')
                self.assertIn(code, self.row(result, domain)['gaps'])
                self.assertEqual(result['releaseVerdict'], 'BLOCKED')

    def test_missing_artifact_hash_future_observation_and_build_binding(self):
        with tempfile.TemporaryDirectory() as parent:
            root = self.fixture(parent)
            for field, value, code in [('artifact',None,'missing-artifact'), ('sha256','f'*64,'artifact-digest-mismatch'),
                                       ('observedAt','2026-10-02T00:00:00Z','stale-or-future-observation')]:
                packet = self.packet(); packet['sections'][1][field] = value
                self.assertIn(code, self.row(self.run_packet(root, packet), 'tests')['gaps'])
            packet = self.packet(); packet['candidate']['build'] = '43'
            for entry in packet['sections']: entry['build'] = '43'
            self.assertIn('build-config-mismatch', self.row(self.run_packet(root, packet), 'tests')['gaps'])

    def test_canonical_evidence_rejects_stale_scope_and_incomplete_attempts(self):
        with tempfile.TemporaryDirectory() as parent:
            root = self.fixture(parent)
            for domain in ('tests','review'):
                packet = self.packet(); path = root / f'{FIXTURES}artifacts/{domain}.json'
                artifact = json.loads(path.read_text())
                if domain == 'tests': artifact['details']['attempts'].pop()
                else: artifact['details']['scopeDigest'] = 'f'*64
                path.write_bytes(canonical(artifact))
                next(e for e in packet['sections'] if e['domain'] == domain)['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                self.assertIn('missing-unsafe-or-invalid-evidence', self.row(self.run_packet(root, packet), domain)['gaps'])

    def test_unsafe_paths_duplicate_domains_fields_and_json_reject(self):
        with tempfile.TemporaryDirectory() as parent:
            root = self.fixture(parent)
            for value in ('../outside.json', '/tmp/outside.json'):
                packet = self.packet(); packet['sections'][1]['artifact'] = value
                self.assertIn('missing-unsafe-or-invalid-evidence', self.row(self.run_packet(root, packet), 'tests')['gaps'])
            packet = self.packet(); packet['sections'].append(copy.deepcopy(packet['sections'][0]))
            with self.assertRaises(Invalid): self.run_packet(root, packet)
            packet = self.packet(); packet['execute'] = 'anything'
            with self.assertRaises(Invalid): self.run_packet(root, packet)
            path = root / f'{FIXTURES}duplicate.json'; path.write_text('{"synthetic":true,"synthetic":true}')
            with self.assertRaises(Invalid): evaluate(path.relative_to(root).as_posix(), root=root)
            target = root / f'{FIXTURES}artifacts/version-build.json'
            outside = Path(parent) / 'outside.json'; outside.write_bytes(target.read_bytes())
            target.unlink(); target.symlink_to(outside)
            self.assertIn('missing-unsafe-or-invalid-evidence', self.row(evaluate(FIXTURES + 'complete.json', root=root), 'version-build')['gaps'])
