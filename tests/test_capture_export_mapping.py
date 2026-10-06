"""Original synthetic mapping tests; no authenticated producer or host is exercised."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from library import ROOT, Invalid, canonical
from check_evaluation_capture import inspect_capture, sha256, MAX_ARTIFACT_BYTES
from map_capture_export import map_export, MAX_PAYLOAD_BYTES, RECORD_PATHS


class CaptureExportMapping(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / 'inputs'
        shutil.copytree(ROOT / 'tests/fixtures/capture-export', self.root)
        self.export = json.loads((self.root / 'export.json').read_text())
        self.policy = json.loads((self.root / 'policy.json').read_text())

    def save(self):
        (self.root / 'export.json').write_bytes(canonical(self.export))

    def mapped(self):
        self.save()
        return map_export('export.json', 'policy.json', self.root)

    def checked(self, report):
        # Only this test materializes declarations; the mapper never writes them.
        for path, record in report['records'].items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(canonical(record))
        return inspect_capture(RECORD_PATHS['manifest'], 'policy.json', self.root)

    def untrusted(self, report):
        self.assertEqual(report['qualificationVerdict'], 'BLOCKED')
        for key in ['trustedEvidence', 'scopeTraceVerified', 'uniqueInvocationVerified',
                    'runtimeInvoked', 'modelInvoked']:
            self.assertIs(report[key], False, key)

    def requests(self, count):
        template = self.export['requests'][0]
        self.export['requests'] = []
        for i in range(count):
            event = copy.deepcopy(template)
            event.update(requestIndex=i + 1, requestId=f'synthetic-request-{i + 1}',
                         requestedAt=f'2030-01-01T00:00:{10 + i * 2:02d}Z',
                         completedAt=f'2030-01-01T00:00:{11 + i * 2:02d}Z')
            self.export['requests'].append(event)
        self.export['claims']['terminalSequence'] = count

    def test_T01_consistent_invented_export_is_deterministic_read_only_and_untrusted(self):
        self.save()
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        report = map_export('export.json', 'policy.json', self.root)
        self.assertEqual(report, map_export('export.json', 'policy.json', self.root))
        self.assertEqual(report['mappingStatus'], 'mapped')
        self.assertEqual(report['findings'], [])
        self.untrusted(report)
        for key in ['producerAuthenticated', 'runtimeQualified', 'executableExportAllowed',
                    'payloadExecuted', 'redactionVerified', 'expiryVerified', 'revocationVerified', 'recordsWritten']:
            self.assertIs(report[key], False)
        self.assertEqual(before, {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.assertFalse((self.root / 'mapped').exists())
        for name in ('request.txt', 'response.txt', 'redacted-request.txt'):
            self.assertNotIn((self.root / 'payloads' / name).read_bytes().strip(), canonical(report))
        checked = self.checked(report)
        self.assertEqual(checked['inventoryStatus'], 'consistent')
        self.untrusted(checked)

    def test_T02_resealed_omission_cannot_be_detected_from_declared_inventory(self):
        self.requests(2)
        complete = self.mapped()
        self.assertEqual(self.checked(complete)['inventoryStatus'], 'consistent')
        self.export['requests'] = self.export['requests'][1:]
        self.export['requests'][0]['requestIndex'] = 1
        self.export['claims']['terminalSequence'] = 1
        forged = self.mapped()
        self.assertEqual(forged['mappingStatus'], 'mapped')
        checked = self.checked(forged)
        self.assertEqual(checked['inventoryStatus'], 'consistent')
        self.untrusted(forged)
        self.untrusted(checked)
        self.assertEqual(forged['records'][RECORD_PATHS['manifest']]['eventCount'], 1)
        loss = next(x for x in forged['fieldLosses'] if x['source'] == 'claims.terminalSequence')
        self.assertEqual(loss['verificationStatus'], 'unverified')

    def test_T03_every_build_outcome_is_preserved_and_incomplete_stays_a_gap(self):
        self.requests(5)
        outcomes = ['success', 'failure', 'denied', 'cancelled', 'incomplete']
        for event, outcome in zip(self.export['requests'], outcomes):
            event['outcome'] = outcome
        self.export['requests'][-1].update(completedAt=None, responseArtifact=None)
        self.export.update(captureStatus='incomplete', closedAt=None)
        report = self.mapped()
        events = report['records'][RECORD_PATHS['transcript']]['events']
        self.assertEqual([e['outcome'] for e in events], outcomes)
        self.assertEqual([e['sequence'] for e in events], [1, 2, 3, 4, 5])
        checked = self.checked(report)
        self.assertEqual(checked['declaredBuildEvents'], 5)
        self.assertEqual(checked['inventoryStatus'], 'gaps')
        self.untrusted(checked)
        self.export['requests'].pop()
        self.export['claims']['terminalSequence'] = 4
        self.export.update(captureStatus='complete', closedAt='2030-01-01T00:00:21Z')
        checked = self.checked(self.mapped())
        self.assertEqual(checked['inventoryStatus'], 'consistent')
        self.assertEqual(checked['declaredBuildEvents'], 4)
        self.untrusted(checked)

    def test_T04_opaque_shell_text_and_wrong_operation_claim_are_never_executed(self):
        data = b'touch capture-mapper-must-not-execute\n'
        (self.root / 'payloads/request.txt').write_bytes(data)
        event = self.export['requests'][0]
        event['requestArtifact']['sha256'] = sha256(data)
        event['operationClaim'] = 'read'
        report = self.mapped()
        self.assertEqual(report['records'][RECORD_PATHS['transcript']]['events'][0]['operation'], 'read')
        self.assertEqual(self.checked(report)['inventoryStatus'], 'consistent')
        self.assertNotIn(data.strip(), canonical(report))
        self.assertFalse((self.root / 'capture-mapper-must-not-execute').exists())
        self.assertFalse((ROOT / 'capture-mapper-must-not-execute').exists())
        self.untrusted(report)

    def test_T05_raw_sanitized_and_review_claims_are_separate_unverified_losses(self):
        report = self.mapped()
        loss = next(x for x in report['fieldLosses'] if x['source'] == 'claims.redaction')
        self.assertEqual(loss['suppliedClaim'], self.export['claims']['redaction'])
        self.assertNotEqual(loss['suppliedClaim']['rawSha256'], loss['suppliedClaim']['sanitizedSha256'])
        self.assertIsNone(loss['canonicalMapping'])
        self.assertEqual(loss['verificationStatus'], 'unverified')
        self.assertFalse(report['redactionVerified'])
        self.assertEqual(len(report['payloadInventory']), 2)
        self.assertNotIn('redaction', report['records'][RECORD_PATHS['admission']])

    def test_T06_policy_subject_and_harness_disagreement_is_not_resealed_away(self):
        original_policy = self.export['policySha256']
        self.policy['budgetSeconds'] = 301
        (self.root / 'policy.json').write_bytes(canonical(self.policy))
        self.export['claims'].update(candidateSha256='d' * 64, scopeSha256='e' * 64, harnessSha256='f' * 64)
        report = self.mapped()
        self.assertEqual(report['mappingStatus'], 'gaps')
        for record in report['records'].values():
            self.assertEqual(record['policySha256'], original_policy)
        self.assertNotEqual(report['identity']['selectedPolicySha256'], original_policy)
        self.assertIn('declared-policy-digest-mismatch', {x['code'] for x in report['findings']})
        self.assertEqual(sum(x['code'] == 'declared-subject-policy-mismatch' for x in report['findings']), 2)
        loss = next(x for x in report['fieldLosses'] if x['source'] == 'claims.harnessSha256')
        self.assertEqual(loss['suppliedClaim'], 'f' * 64)
        self.assertEqual(loss['verificationStatus'], 'unverified')
        self.assertIn('policy-digest-mismatch', {x['code'] for x in self.checked(report)['findings']})
        self.untrusted(report)

    def test_T07_expiry_revocation_and_missing_claims_never_authenticate_evidence(self):
        for expiry, revoked in [('1900-01-01T00:00:00Z', True), (None, None), ('2030-01-02T00:00:00Z', False)]:
            self.export['claims'].update(expiresAt=expiry, revoked=revoked, producerId=None, harnessSha256=None)
            with self.subTest(expiry=expiry, revoked=revoked):
                report = self.mapped()
                self.assertEqual(report['mappingStatus'], 'mapped')
                claims = {x['source']: x['suppliedClaim'] for x in report['fieldLosses']}
                self.assertEqual(claims['claims.expiresAt'], expiry)
                self.assertEqual(claims['claims.revoked'], revoked)
                self.assertTrue(all(x['verificationStatus'] == 'unverified' for x in report['fieldLosses']))
                self.assertFalse(report['expiryVerified'])
                self.assertFalse(report['revocationVerified'])
                self.assertEqual(self.checked(report)['inventoryStatus'], 'consistent')
                self.untrusted(report)

    def test_closed_synthetic_contract_rejects_unknown_version_fields_and_boolean_counts(self):
        original = copy.deepcopy(self.export)
        variants = [{**original, 'origin': 'live-producer'}, {**original, 'schemaVersion': '2'},
                    {**original, 'policy': self.policy}, {**original, 'unknown': True}]
        for key, value in [('terminalSequence', True), ('expiresAt', '2030-01-01')]:
            variant = copy.deepcopy(original)
            variant['claims'][key] = value
            variants.append(variant)
        variant = copy.deepcopy(original); variant['requests'][0]['requestIndex'] = True
        variants.append(variant)
        variant = copy.deepcopy(original); variant['requests'] *= 501
        variants.append(variant)
        variant = copy.deepcopy(original); variant['claims']['authenticated'] = True
        variants.append(variant)
        for variant in variants:
            self.export = variant
            with self.subTest(variant=variant), self.assertRaises(Invalid):
                self.mapped()

    def test_payload_digests_missing_paths_symlinks_and_reserved_outputs_do_not_read_or_write(self):
        original = copy.deepcopy(self.export)
        outside = self.root.parent / 'outside.txt'
        outside.write_text('Original synthetic outside file; no private data.\n')
        (self.root / 'payloads/link.txt').symlink_to(outside)
        for path in ['../outside.txt', str(outside), 'file://outside', 'payloads/link.txt', 'payloads/missing.txt']:
            self.export = copy.deepcopy(original)
            self.export['requests'][0]['requestArtifact']['path'] = path
            with self.subTest(path=path):
                opened = []
                original_open = Path.open
                def record_open(target, *args, **kwargs):
                    opened.append(target)
                    return original_open(target, *args, **kwargs)
                with patch.object(Path, 'open', record_open):
                    report = self.mapped()
                self.assertEqual(report['mappingStatus'], 'gaps')
                self.assertNotIn(outside.resolve(), [p.resolve() for p in opened])
                self.assertEqual(report['payloadBytesRead'], (self.root / 'payloads/response.txt').stat().st_size)
                self.assertNotIn('Original synthetic outside file', canonical(report).decode())
                self.assertFalse((self.root / 'mapped').exists())
        self.export = copy.deepcopy(original)
        self.export['requests'][0]['requestArtifact']['sha256'] = '0' * 64
        self.assertIn('payload-digest-mismatch', {x['code'] for x in self.mapped()['findings']})
        (self.root / 'mapped').write_text('Original synthetic reserved namespace collision.\n')
        for path in ['mapped', 'mapped/admission.json', 'Mapped', 'Mapped/admission.json']:
            self.export['requests'][0]['requestArtifact']['path'] = path
            with self.subTest(path=path), self.assertRaisesRegex(Invalid, 'reserved'):
                self.mapped()

    def test_zero_reordered_and_duplicate_events_stay_visible_to_existing_checker(self):
        self.requests(2)
        self.export['requests'].reverse()
        checked = self.checked(self.mapped())
        self.assertIn('event-sequence-mismatch', {x['code'] for x in checked['findings']})
        self.requests(2)
        self.export['requests'][1]['requestId'] = self.export['requests'][0]['requestId']
        self.assertIn('duplicate-request-id', {x['code'] for x in self.checked(self.mapped())['findings']})
        self.requests(0)
        self.assertIn('empty-event-sequence', {x['code'] for x in self.checked(self.mapped())['findings']})

    def test_all_actual_payload_read_bytes_are_bounded_including_rejected_repeats(self):
        data = b'x' * MAX_ARTIFACT_BYTES
        self.requests(5)
        for i, event in enumerate(self.export['requests']):
            path = f'payloads/large-{i}.txt'
            (self.root / path).write_bytes(data)
            ref = {'path': path, 'sha256': sha256(data)}
            event.update(requestArtifact=ref, responseArtifact=copy.deepcopy(ref))
        report = self.mapped()
        self.assertEqual(report['payloadBytesRead'], MAX_PAYLOAD_BYTES)
        self.assertEqual(len(report['payloadInventory']), 4)
        self.assertIn('payload-total-budget-exceeded', {x['code'] for x in report['findings']})
        data += b'x'
        (self.root / 'payloads/oversize.txt').write_bytes(data)
        for event in self.export['requests']:
            ref = {'path': 'payloads/oversize.txt', 'sha256': sha256(data)}
            event.update(requestArtifact=ref, responseArtifact=copy.deepcopy(ref))
        report = self.mapped()
        self.assertLessEqual(report['payloadBytesRead'], MAX_PAYLOAD_BYTES)
        self.assertEqual(report['payloadInventory'], [])
        self.assertIn('payload-size-limit-exceeded', {x['code'] for x in report['findings']})

    def test_duplicate_json_invalid_input_and_strict_timestamps_reject(self):
        for raw in [b'{"kind":1,"kind":2}', b'\xff', b'[' * 1200]:
            (self.root / 'export.json').write_bytes(raw)
            with self.subTest(raw=raw[:10]), self.assertRaises(Invalid):
                map_export('export.json', 'policy.json', self.root)
        self.export['startedAt'] = '2030-02-30T00:00:00Z'
        with patch('jsonschema._format.FormatChecker.checkers', {}), self.assertRaises(Invalid):
            self.mapped()
        self.export['startedAt'] = '2030-01-01T00:00:00Z'
        self.policy['startedAt'] = '2030-02-30T00:00:00Z'
        (self.root / 'policy.json').write_bytes(canonical(self.policy))
        with patch('jsonschema._format.FormatChecker.checkers', {}), self.assertRaises(Invalid):
            self.mapped()
        (self.root / 'export.json').write_bytes(b' ' * (MAX_ARTIFACT_BYTES + 1))
        with self.assertRaisesRegex(Invalid, '4 MiB'):
            map_export('export.json', 'policy.json', self.root)

    def test_CLI_exit_zero_one_two_and_no_payload_or_output_file_side_effects(self):
        def cli(expected):
            result = subprocess.run([sys.executable, '-B', 'tools/map_capture_export.py', 'export.json',
                                     '--policy', 'policy.json', '--root', str(self.root)],
                                    cwd=ROOT, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, expected, result.stderr)
            self.assertNotIn('Traceback', result.stderr)
            self.assertFalse((self.root / 'mapped').exists())
            return result
        self.save()
        first = cli(0)
        self.assertEqual(first.stdout, cli(0).stdout)
        self.untrusted(json.loads(first.stdout))
        self.export['requests'][0]['requestArtifact']['sha256'] = '0' * 64
        self.save()
        self.assertEqual(json.loads(cli(1).stdout)['mappingStatus'], 'gaps')
        self.export['origin'] = 'live-producer'
        self.save()
        invalid = cli(2)
        self.assertEqual(invalid.stdout, '')
        self.assertTrue(invalid.stderr.startswith('Invalid export:'))

    def test_CLI_rejects_unpaired_unicode_in_export_and_policy_without_traceback(self):
        original_export = copy.deepcopy(self.export)
        original_policy = copy.deepcopy(self.policy)
        for location in ['evaluationId', 'producerId', 'payloadPath', 'policyModel']:
            self.export = copy.deepcopy(original_export)
            self.policy = copy.deepcopy(original_policy)
            if location == 'evaluationId':
                self.export['evaluationId'] = '\ud800'
            elif location == 'producerId':
                self.export['claims']['producerId'] = '\ud800'
            elif location == 'payloadPath':
                self.export['requests'][0]['requestArtifact']['path'] = '\ud800'
            else:
                self.policy['model'] = '\ud800'
            # JSON escapes preserve the malformed string for the CLI parser.
            (self.root / 'export.json').write_text(json.dumps(self.export))
            (self.root / 'policy.json').write_text(json.dumps(self.policy))
            result = subprocess.run([sys.executable, '-B', 'tools/map_capture_export.py', 'export.json',
                                     '--policy', 'policy.json', '--root', str(self.root)],
                                    cwd=ROOT, capture_output=True, text=True, timeout=15)
            with self.subTest(location=location):
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, '')
                self.assertEqual(result.stderr, 'Invalid export: synthetic export or selected policy contains invalid Unicode\n')
                self.assertFalse((self.root / 'mapped').exists())
        self.export = original_export
        self.policy = original_policy
        self.export['claims']['producerId'] = 'synthetic-\U0001f680'
        (self.root / 'policy.json').write_bytes(canonical(self.policy))
        self.export['policySha256'] = sha256(canonical(self.policy))
        report = self.mapped()
        self.assertEqual(report['mappingStatus'], 'mapped')
        self.assertEqual(next(x['suppliedClaim'] for x in report['fieldLosses'] if x['source'] == 'claims.producerId'),
                         'synthetic-\U0001f680')
        self.untrusted(report)


if __name__ == '__main__':
    unittest.main()
