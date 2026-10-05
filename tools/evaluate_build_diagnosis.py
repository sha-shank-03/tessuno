#!/usr/bin/env python3
"""Score structured answers against original synthetic logs; never invoke Xcode or a model."""
import argparse
import hashlib
from pathlib import Path
import sys
from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from library import ROOT, Invalid, canonical, read_json, safe_path

CASES = ('unresolved-symbol', 'missing-module', 'incomplete-log', 'multiple-diagnostics', 'mixed-diagnostics')
HYPOTHESIS_DIAGNOSTICS = {
    'symbol-name-mismatch': 'unresolved-symbol',
    'missing-source-declaration': 'unresolved-symbol',
    'target-dependency-missing': 'missing-module',
    'insufficient-context': 'insufficient-log',
}
SCHEMA = 'skills/xcode-build-diagnosis/response.schema.json'
ASSERTIONS = ('response-schema', 'case-id', 'exact-citations', 'complete-observations',
              'bounded-hypotheses', 'bounded-next-steps', 'required-context-gaps')


def no_refs(value):
    if isinstance(value, dict):
        if set(value) & {'$ref', '$dynamicRef', '$recursiveRef'}:
            raise Invalid('diagnosis response schema references are unsupported')
        for item in value.values(): no_refs(item)
    elif isinstance(value, list):
        for item in value: no_refs(item)


def evaluate(case_id, response, root=ROOT):
    if case_id not in CASES:
        raise Invalid('unknown synthetic diagnosis case')
    case_path = safe_path(root, 'evals/xcode-build-diagnosis/cases/' + case_id + '.json')
    case = read_json(case_path)
    if case.get('caseId') != case_id or case.get('origin') != 'original-synthetic':
        raise Invalid('case identity/origin mismatch')
    log_path = safe_path(root, case['log']); log = log_path.read_text().splitlines()
    schema_path = safe_path(root, SCHEMA); schema = read_json(schema_path); no_refs(schema)
    try: Draft202012Validator.check_schema(schema)
    except SchemaError as error: raise Invalid('invalid diagnosis response schema') from error
    errors = sorted(Draft202012Validator(schema).iter_errors(response), key=lambda error: str(error.path))
    results = [{'id': key, 'status': 'blocked'} for key in ASSERTIONS]
    results[0]['status'] = 'fail' if errors else 'pass'
    if errors:
        results[0]['details'] = ['Schema violation at ' + str(list(error.path)) for error in errors]
    else:
        expected = case['expected']
        observed = [(item['code'], item['logLine']) for item in response['observations']]
        wanted = [(item['code'], item['logLine']) for item in expected['observations']]
        matching = set(observed) & set(wanted)
        evidence_lines = {family: {line for code, line in matching if code == family}
                          for family in set(HYPOTHESIS_DIAGNOSTICS.values())}
        actions = {item['action'] for item in response['nextSteps']}
        checks = [
            response['caseId'] == case_id,
            all(1 <= item['logLine'] <= len(log) and item['quote'] == log[int(item['logLine']) - 1]
                for item in response['observations']),
            len(observed) == len(set(observed)) and set(observed) == set(wanted),
            all(item['code'] in expected['allowedHypotheses'] and set(item['evidenceLines']) <=
                evidence_lines.get(HYPOTHESIS_DIAGNOSTICS.get(item['code']), set())
                for item in response['hypotheses']),
            set(expected['requiredActions']) <= actions <= set(expected['allowedActions']),
            set(expected['requiredMissingInputs']) <= set(response['missingInputs']),
        ]
        for result, passed in zip(results[1:], checks): result['status'] = 'pass' if passed else 'fail'
    passed = sum(item['status'] == 'pass' for item in results)
    return {'caseId': case_id, 'scope': 'synthetic-structured-response-only',
            'status': 'pass' if passed == len(results) else 'fail',
            'modelInvokedByScorer': False, 'xcodeInvokedByScorer': False,
            'assertionsTotal': len(results),
            'assertionsExecuted': sum(item['status'] != 'blocked' for item in results),
            'assertionsPassed': passed, 'assertions': results,
            'identity': {'caseSha256': hashlib.sha256(case_path.read_bytes()).hexdigest(),
                         'logSha256': hashlib.sha256(log_path.read_bytes()).hexdigest(),
                         'responseSha256': hashlib.sha256(canonical(response)).hexdigest(),
                         'schemaSha256': hashlib.sha256(schema_path.read_bytes()).hexdigest(),
                         'scorerSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--examples', action='store_true', help='Score all hand-authored synthetic examples')
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--diagnosis', help='Repository-relative JSON response file; symlinks forbidden')
    args = parser.parse_args(argv)
    if args.examples and (args.case or args.diagnosis): parser.error('--examples cannot be combined with input flags')
    if not args.examples and not (args.case and args.diagnosis): parser.error('supply --examples or both --case and --diagnosis')
    try:
        if args.examples:
            reports = [evaluate(case, read_json(safe_path(ROOT, 'skills/xcode-build-diagnosis/examples/' + case + '.json')))
                       for case in CASES]
        else:
            reports = [evaluate(args.case, read_json(safe_path(ROOT, args.diagnosis)))]
        sys.stdout.buffer.write(canonical(reports))
        return 0 if all(report['status'] == 'pass' for report in reports) else 1
    except (Invalid, OSError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__': sys.exit(main())
