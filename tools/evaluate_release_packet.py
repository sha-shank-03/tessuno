"""Deterministic authored-packet inventory checks; no release/runtime authority."""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from library import (ROOT, Invalid, safe_path, read_json, checked_schema, evidence_check,
                     Draft202012Validator, FormatChecker, digest)

DOMAINS = ('version-build', 'tests', 'review', 'testflight-feedback', 'crashes',
           'metadata-privacy', 'migrations', 'mitigation')
FIXTURES = 'skills/release-readiness-evidence/fixtures/'


def utc(value):
    try:
        parsed = datetime.fromisoformat(value.upper().replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError('timestamp must include a timezone')
        return parsed.astimezone(timezone.utc)
    except (AttributeError, TypeError, ValueError, OverflowError) as error:
        raise Invalid('unsupported timestamp') from error


def evaluate(packet_path, root=ROOT):
    path = safe_path(root, packet_path)
    packet = read_json(path)
    schema = checked_schema(root, 'release-packet')
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(packet))
    if errors:
        raise Invalid('invalid synthetic release packet: ' + '; '.join(e.message for e in errors))
    sections = {entry['domain']: entry for entry in packet['sections']}
    if len(sections) != len(packet['sections']):
        raise Invalid('duplicate release domain')
    candidate = packet['candidate']
    as_of = utc(packet['asOf'])
    # Reuse canonical subject definitions directly; no unrelated fixture is required.
    evidence_schema = checked_schema(root, 'evidence')
    subject_schema = {'$schema': evidence_schema['$schema'], '$defs': evidence_schema['$defs'],
                      **evidence_schema['properties']['subject']}
    subject_errors = list(Draft202012Validator(subject_schema, format_checker=FormatChecker())
                          .iter_errors(candidate['subject']))
    if subject_errors:
        raise Invalid('invalid candidate subject: ' + '; '.join(e.message for e in subject_errors))
    if candidate['subject']['version'] != candidate['version']:
        raise Invalid('candidate version and subject version disagree')
    config_digest = digest({key: candidate[key] for key in ('version', 'build', 'scopeDigest')})
    rows = []
    for domain in DOMAINS:
        entry = sections.get(domain)
        gaps = []
        def gap(code):
            gaps.append(code)
        if entry is None:
            gap('missing-domain')
        else:
            if entry['version'] != candidate['version'] or entry['build'] != candidate['build']:
                gap('version-build-mismatch')
            if entry['candidateDigest'] != candidate['subject']['sha256'] or entry['scopeDigest'] != candidate['scopeDigest']:
                gap('candidate-scope-mismatch')
            age = as_of - utc(entry['observedAt'])
            if age < timedelta(0) or age > timedelta(days=14):
                gap('stale-or-future-observation')
            if entry['outcome'] != 'reported-pass':
                gap(entry['outcome'])
            if entry['artifact'] is None or entry['sha256'] is None:
                gap('missing-artifact')
            else:
                try:
                    artifact_path = safe_path(root, entry['artifact'])
                    if hashlib.sha256(artifact_path.read_bytes()).hexdigest() != entry['sha256']:
                        gap('artifact-digest-mismatch')
                    else:
                        artifact = read_json(artifact_path)
                        if not isinstance(artifact, dict):
                            raise Invalid('artifact must be an object')
                        if domain in ('tests', 'review'):
                            if artifact.get('category') != ('execution' if domain == 'tests' else 'human-review'):
                                raise Invalid('wrong evidence category')
                            evidence_check(artifact, expected_subject=candidate['subject'],
                                scope_digest=candidate['scopeDigest'],
                                expected_attempts=packet['plannedTests'] if domain == 'tests' else None)
                            if utc(artifact['createdAt']) != utc(entry['observedAt']):
                                gap('observation-time-mismatch')
                            if artifact['check']['configDigest'] != config_digest:
                                gap('build-config-mismatch')
                            if artifact['status'] != 'pass':
                                gap('evidence-not-pass')
                        else:
                            expected = {'synthetic': True, 'domain': domain, 'version': entry['version'],
                                        'build': entry['build'], 'candidateDigest': entry['candidateDigest'],
                                        'scopeDigest': entry['scopeDigest']}
                            if (any(artifact.get(key) != value for key, value in expected.items())
                                    or utc(artifact.get('observedAt')) != utc(entry['observedAt'])):
                                gap('artifact-identity-mismatch')
                except Invalid:
                    gap('missing-unsafe-or-invalid-evidence')
        rows.append({'domain': domain, 'inventoryStatus': 'gap' if gaps else 'declared-evidence-present',
                     'artifact': entry['artifact'] if entry else None, 'gaps': gaps,
                     'provenance': 'unverified'})
    return {'packetSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'policy': 'synthetic inventory only; 14-day illustrative window',
            'policyDigest': digest({'domains': DOMAINS, 'maxAgeDays': 14}),
            'inventoryStatus': 'gaps' if any(row['gaps'] for row in rows) else 'complete',
            'domains': rows, 'releaseVerdict': 'BLOCKED', 'trustedEvidence': False,
            'runtimeInvoked': False, 'modelInvoked': False,
            'limitations': ['Authored synthetic inputs; completeness is not app qualification or release approval.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', help='repository-relative original synthetic packet')
    args = parser.parse_args()
    try:
        result = evaluate(args.packet)
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['inventoryStatus'] == 'complete' else 1)
    except Invalid as error:
        parser.exit(2, f'Invalid packet: {error}\n')
