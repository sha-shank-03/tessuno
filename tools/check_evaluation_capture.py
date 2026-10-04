"""Inspect supplied capture bytes offline; never collect, execute or authenticate them."""
import argparse
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
import sys

from library import (ROOT, Invalid, canonical, checked_schema, no_duplicates, safe_path,
                     Draft202012Validator, FormatChecker)

MAX_ARTIFACT_BYTES = 4 * 1024 * 1024
UTC_PATTERN = r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]{1,6})?Z'


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_bytes(root, relative):
    path = safe_path(root, relative)
    with path.open('rb') as stream:
        data = stream.read(MAX_ARTIFACT_BYTES + 1)
    if len(data) > MAX_ARTIFACT_BYTES:
        raise Invalid('capture artifact exceeds 4 MiB limit')
    return data


def document(data, kind, schema):
    try:
        value = json.loads(data, object_pairs_hook=no_duplicates)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise Invalid('invalid capture JSON') from error
    contract = {'$schema': schema['$schema'], '$defs': schema['$defs'],
                '$ref': '#/$defs/' + kind}
    if not Draft202012Validator(contract, format_checker=FormatChecker()).is_valid(value):
        raise Invalid('invalid ' + kind + ' contract')
    return value


def utc(value):
    try:
        # FormatChecker's date-time validation is an optional dependency. Check the
        # accepted syntax and precision explicitly before datetime can truncate it.
        if not isinstance(value, str) or re.fullmatch(UTC_PATTERN, value) is None:
            raise ValueError('timestamp must be strict UTC with at most microsecond precision')
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (TypeError, ValueError, OverflowError) as error:
        raise Invalid('unsupported capture timestamp') from error


def inspect_capture(manifest_path, policy_path, root=ROOT):
    """Compare with a separately selected policy; authenticity remains unverified."""
    schema = checked_schema(ROOT, 'evaluation-capture')
    policy_bytes = read_bytes(root, policy_path)
    manifest_bytes = read_bytes(root, manifest_path)
    policy = document(policy_bytes, 'policy', schema)
    manifest = document(manifest_bytes, 'manifest', schema)
    policy_hash = sha256(policy_bytes)
    findings = []

    def gap(code, location):
        findings.append({'code': code, 'location': location})

    def identity(value, location):
        if value['evaluationId'] != policy['evaluationId']:
            gap('evaluation-id-mismatch', location)
        if value['policySha256'] != policy_hash:
            gap('policy-digest-mismatch', location)

    def artifact(ref, location, kind=None):
        if ref is None:
            gap('missing-artifact', location)
            return None
        try:
            data = read_bytes(root, ref['path'])
            if sha256(data) != ref['sha256']:
                gap('artifact-digest-mismatch', location)
                return None
            return document(data, kind, schema) if kind else data
        except (Invalid, OSError):
            gap('missing-unsafe-or-invalid-artifact', location)
            return None

    identity(manifest, 'manifest')
    start = utc(policy['startedAt'])
    try:
        deadline = start + timedelta(seconds=policy['budgetSeconds'])
    except OverflowError as error:
        raise Invalid('capture deadline is out of range') from error
    admission = artifact(manifest['admission'], 'admission', 'admission')
    transcript = artifact(manifest['transcript'], 'transcript', 'transcript')
    if admission is not None:
        identity(admission, 'admission')
        for field in ('startedAt', 'model', 'contextMode'):
            if admission[field] != policy[field]:
                gap('admission-policy-mismatch', 'admission.' + field)
    builds = 0
    if transcript is not None:
        identity(transcript, 'transcript')
        if admission is not None:
            for field in ('taskId', 'turnId'):
                if transcript[field] != admission[field]:
                    gap('admission-transcript-mismatch', 'transcript.' + field)
        events = transcript['events']
        if len(events) != manifest['eventCount']:
            gap('event-count-mismatch', 'transcript')
        if not events:
            gap('empty-event-sequence', 'transcript')
        closed = utc(transcript['closedAt']) if transcript['closedAt'] else None
        if transcript['captureStatus'] != 'complete' or closed is None:
            gap('incomplete-transcript', 'transcript')
        if closed is not None and not start <= closed <= deadline:
            gap('closure-outside-budget', 'transcript.closedAt')
        request_ids = set()
        previous = start
        for index, event in enumerate(events, 1):
            location = 'events[' + str(index) + ']'
            if event['sequence'] != index:
                gap('event-sequence-mismatch', location)
            if event['requestId'] in request_ids:
                gap('duplicate-request-id', location)
            request_ids.add(event['requestId'])
            requested = utc(event['requestedAt'])
            completed = utc(event['completedAt']) if event['completedAt'] else None
            if requested < previous or not start <= requested <= deadline:
                gap('request-time-out-of-order-or-budget', location)
            previous = requested
            if completed is None or event['outcome'] == 'incomplete':
                gap('incomplete-event', location)
            if completed is not None and not requested <= completed <= deadline:
                gap('completion-time-out-of-order-or-budget', location)
            if closed is not None and (requested > closed or (completed is not None and completed > closed)):
                gap('event-after-closure', location)
            artifact(event['request'], location + '.request')
            artifact(event['response'], location + '.response')
            if event['operation'] == 'build':
                builds += 1
                if completed is not None and (completed - requested).total_seconds() > policy['maxBuildSeconds']:
                    gap('build-duration-exceeded', location)
        if builds > policy['maxBuildInvocations']:
            gap('declared-build-count-exceeded', 'transcript')
    return {
        'inventoryStatus': 'gaps' if findings else 'consistent',
        'findings': findings, 'declaredBuildEvents': builds,
        'identity': {'manifestSha256': sha256(manifest_bytes), 'policySha256': policy_hash,
                     'schemaSha256': sha256(safe_path(ROOT, 'schemas/evaluation-capture.schema.json').read_bytes()),
                     'checkerSha256': sha256(Path(__file__).read_bytes())},
        'trustedEvidence': False, 'scopeTraceVerified': False,
        'uniqueInvocationVerified': False, 'qualificationVerdict': 'BLOCKED',
        'runtimeInvoked': False, 'modelInvoked': False,
        'limitations': [
            'Supplied records, event classifications and timestamps are declarations, not authenticated observation.',
            'Matching bytes and sequence do not prove that all real tool requests or attempts were captured.',
            'Policy selection, immutable launch provenance, redaction and approval boundaries need independent verification.',
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', help='root-relative capture manifest; no symlinks')
    parser.add_argument('--policy', required=True, help='separately selected root-relative frozen policy')
    parser.add_argument('--root', type=Path, default=ROOT, help='sanitized capture directory (default: repository)')
    args = parser.parse_args(argv)
    try:
        report = inspect_capture(args.manifest, args.policy, args.root)
        sys.stdout.buffer.write(canonical(report))
        return 0 if report['inventoryStatus'] == 'consistent' else 1
    except (Invalid, OSError) as error:
        print('Invalid capture: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
