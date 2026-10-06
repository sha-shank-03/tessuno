"""Map an original synthetic local export; never collect, execute or authenticate it."""
import argparse
import json
from os import fstat
from pathlib import Path
import sys

from check_evaluation_capture import document, read_bytes, sha256, utc, MAX_ARTIFACT_BYTES
from library import (ROOT, Invalid, canonical, checked_schema, no_duplicates, safe_path,
                     Draft202012Validator, FormatChecker)

MAX_PAYLOAD_BYTES = 16 * 1024 * 1024
RECORD_PATHS = {'admission': 'mapped/admission.json', 'transcript': 'mapped/transcript.json',
                'manifest': 'mapped/manifest.json'}
LOSS_REASONS = {
    'producerId': 'A supplied identifier does not authenticate the producer.',
    'harnessSha256': 'Supplied harness bytes are not independently approved or authenticated.',
    'candidateSha256': 'Candidate identity is a declaration, not a reconstructed or authenticated closure.',
    'scopeSha256': 'Scope identity is a declaration, not observed enforcement.',
    'terminalSequence': 'A contributor-supplied terminal bound cannot prove all real requests were captured.',
    'approval': 'A supplied approval label grants no action authority.',
    'redaction': 'Raw/sanitized hashes and a review label do not verify redaction or lineage.',
    'expiresAt': 'No trusted clock, authenticated producer or expiry policy is evaluated.',
    'revoked': 'No independently authenticated revocation source is consulted.',
}


def map_export(export_path, policy_path, root=ROOT):
    """Return records/report only; no output files, payload execution or trust decision."""
    export_bytes = read_bytes(root, export_path)
    policy_bytes = read_bytes(root, policy_path)
    capture_schema = checked_schema(ROOT, 'evaluation-capture')
    export_schema = checked_schema(ROOT, 'capture-export')
    policy = document(policy_bytes, 'policy', capture_schema)
    try:
        export = json.loads(export_bytes, object_pairs_hook=no_duplicates)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise Invalid('invalid synthetic export JSON') from error
    if not Draft202012Validator(export_schema, format_checker=FormatChecker()).is_valid(export):
        raise Invalid('invalid synthetic export contract')
    try:
        # Escaped unpaired surrogates parse as JSON strings but cannot enter our
        # canonical UTF-8 records, loss report or filesystem paths.
        canonical(export)
        canonical(policy)
    except UnicodeError as error:
        raise Invalid('synthetic export or selected policy contains invalid Unicode') from error
    for value in [policy['startedAt'], export['startedAt'], export['closedAt'], export['claims']['expiresAt']]:
        if value is not None:
            utc(value)
    for request in export['requests']:
        utc(request['requestedAt'])
        if request['completedAt'] is not None:
            utc(request['completedAt'])
    identity = {key: export[key] for key in ('evaluationId', 'policySha256')}
    task = {key: export[key] for key in ('taskId', 'turnId')}
    admission = {'schemaVersion': '1', 'kind': 'task-admission', **identity, **task,
                 **{key: export[key] for key in ('startedAt', 'model', 'contextMode')}}
    events = [{'sequence': r['requestIndex'], 'requestId': r['requestId'], 'tool': r['toolName'],
               'operation': r['operationClaim'], 'requestedAt': r['requestedAt'],
               'completedAt': r['completedAt'], 'outcome': r['outcome'],
               'request': r['requestArtifact'], 'response': r['responseArtifact']}
              for r in export['requests']]
    transcript = {'schemaVersion': '1', 'kind': 'tool-transcript', **identity, **task,
                  'captureStatus': export['captureStatus'], 'closedAt': export['closedAt'],
                  'events': events}
    manifest = {'schemaVersion': '1', 'kind': 'capture-manifest', **identity,
                'admission': {'path': RECORD_PATHS['admission'], 'sha256': sha256(canonical(admission))},
                'transcript': {'path': RECORD_PATHS['transcript'], 'sha256': sha256(canonical(transcript))},
                'eventCount': len(events)}
    for value, kind in [(admission, 'admission'), (transcript, 'transcript'), (manifest, 'manifest')]:
        document(canonical(value), kind, capture_schema)
    findings = []
    def gap(code, location):
        findings.append({'code': code, 'location': location})
    if export['policySha256'] != sha256(policy_bytes):
        gap('declared-policy-digest-mismatch', 'policySha256')
    for field in ('evaluationId', 'startedAt', 'model', 'contextMode'):
        if export[field] != policy[field]:
            gap('declared-admission-policy-mismatch', field)
    for field in ('candidateSha256', 'scopeSha256'):
        claim = export['claims'][field]
        if claim is not None and claim != policy[field]:
            gap('declared-subject-policy-mismatch', 'claims.' + field)
    terminal = export['claims']['terminalSequence']
    if terminal is not None and terminal != (events[-1]['sequence'] if events else 0):
        gap('declared-terminal-sequence-mismatch', 'claims.terminalSequence')
    consumed = {}
    total = 0
    exhausted = False
    for index, event in enumerate(events, 1):
        for field in ('request', 'response'):
            ref = event[field]
            location = f'events[{index}].{field}'
            if ref is None:
                gap('missing-payload-reference', location)
                continue
            if ref['path'].split('/', 1)[0].casefold() == 'mapped':
                raise Invalid('payload collides with reserved mapped record paths')
            if ref['path'] not in consumed:
                if exhausted:
                    gap('payload-total-budget-exceeded', location)
                    continue
                try:
                    path = safe_path(root, ref['path'])
                    remaining = MAX_PAYLOAD_BYTES - total
                    if remaining == 0:
                        exhausted = True
                        gap('payload-total-budget-exceeded', location)
                        continue
                    with path.open('rb') as stream:
                        data = stream.read(min(MAX_ARTIFACT_BYTES + 1, remaining))
                        total += len(data)
                        size = fstat(stream.fileno()).st_size
                    exhausted = total == MAX_PAYLOAD_BYTES
                    if len(data) > MAX_ARTIFACT_BYTES:
                        gap('payload-size-limit-exceeded', location)
                        continue
                    if size > len(data):
                        gap('payload-total-budget-exceeded' if exhausted else 'payload-size-limit-exceeded', location)
                        continue
                    consumed[ref['path']] = {'sha256': sha256(data), 'bytes': len(data)}
                except (Invalid, OSError):
                    gap('missing-or-unsafe-payload', location)
                    continue
            if consumed[ref['path']]['sha256'] != ref['sha256']:
                gap('payload-digest-mismatch', location)
    records = {RECORD_PATHS['admission']: admission, RECORD_PATHS['transcript']: transcript,
               RECORD_PATHS['manifest']: manifest}
    losses = [{'source': 'claims.' + field, 'suppliedClaim': export['claims'][field],
               'canonicalMapping': None, 'verificationStatus': 'unverified', 'reason': reason}
              for field, reason in LOSS_REASONS.items()]
    return {
        'mappingStatus': 'gaps' if findings else 'mapped', 'inputOriginClaim': export['origin'],
        'findings': findings, 'records': records, 'fieldLosses': losses,
        'payloadInventory': [{'path': path, **entry} for path, entry in sorted(consumed.items())],
        'payloadBytesRead': total, 'payloadByteBudget': MAX_PAYLOAD_BYTES,
        'identity': {'exportSha256': sha256(export_bytes), 'selectedPolicySha256': sha256(policy_bytes),
                     **{name: sha256(safe_path(ROOT, path).read_bytes()) for name, path in [
                         ('mapperSha256', 'tools/map_capture_export.py'),
                         ('checkerSha256', 'tools/check_evaluation_capture.py'),
                         ('librarySha256', 'tools/library.py'),
                         ('exportSchemaSha256', 'schemas/capture-export.schema.json'),
                         ('captureSchemaSha256', 'schemas/evaluation-capture.schema.json')]}},
        'trustedEvidence': False, 'scopeTraceVerified': False, 'uniqueInvocationVerified': False,
        'runtimeQualified': False, 'executableExportAllowed': False, 'qualificationVerdict': 'BLOCKED',
        'runtimeInvoked': False, 'modelInvoked': False, 'payloadExecuted': False,
        'producerAuthenticated': False, 'redactionVerified': False, 'expiryVerified': False,
        'revocationVerified': False, 'recordsWritten': False,
        'limitations': [
            'The synthetic origin marker and every metadata value are supplied claims.',
            'Mapped records are declarations; run the separate offline checker for inventory comparisons.',
            'A contributor can remove/relabel requests and reseal all hashes and terminal claims.',
            'No real producer, host enforcement, approval, complete capture or protected policy is verified.',
            'Stable snapshot required; path/byte limits are not OS containment or redaction.',
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('export', help='root-relative original synthetic export; no symlinks')
    parser.add_argument('--policy', required=True, help='separately selected policy path')
    parser.add_argument('--root', type=Path, default=ROOT, help='immutable sanitized local input root')
    args = parser.parse_args(argv)
    try:
        report = map_export(args.export, args.policy, args.root)
        sys.stdout.buffer.write(canonical(report))
        return 0 if report['mappingStatus'] == 'mapped' else 1
    except (Invalid, OSError) as error:
        print('Invalid export: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
