#!/usr/bin/env python3
"""Export offline adapter inspection data, never executable host configuration."""
import argparse
import hashlib
from pathlib import Path
import sys

from library import ROOT, Invalid, adapter_report, canonical, closure, digest, load_catalog, safe_path, subject_manifest

TOOL_ROOT = Path(__file__).resolve().parents[1]


def inspect_adapter(agent_id, root=ROOT, host='codex', executable=False):
    if not isinstance(agent_id, str):
        raise Invalid('inspection requires an exact catalog Agent id')
    if host != 'codex':
        raise Invalid('unsupported inspection host; only codex is documented')
    records = load_catalog(root)
    info = records.get(agent_id)
    if info is None or info['record']['kind'] != 'Agent':
        raise Invalid('inspection requires an exact catalog Agent id')
    record = info['record']
    report = adapter_report(record)
    if executable:
        raise Invalid('executable export rejected: unsupported controls: ' +
                      ', '.join(report['unsupported']) + '; trusted enforcement verification unavailable')
    subject, manifest, lock, _ = subject_manifest(root, records, agent_id)
    # Bind the running exporter/validator sources, consumed schemas and dependency lock.
    # These hashes identify bytes, not an authenticated or protected generator.
    sources = {'tool': (TOOL_ROOT, ['tools/export_adapter.py', 'requirements-dev.lock']),
               'validator': (ROOT, ['tools/library.py', 'schemas/agent.schema.json']),
               'catalog': (root, ['schemas/' + name + '.schema.json' for name in
                                 ['common', 'agent', 'skill', 'recipe', 'pack', 'evidence']])}
    files = [{'source': source, 'path': path,
              'sha256': hashlib.sha256(safe_path(base, path).read_bytes()).hexdigest()}
             for source, (base, paths) in sorted(sources.items()) for path in sorted(paths)]
    permission_keys = ['filesystemScope', 'networkScope', 'requiredTools',
                       'humanApprovalRequirements', 'requiredControls']
    components = []
    for key in closure(records, agent_id):
        component = records[key]['record']
        components.append({**{field: component[field] for field in ['kind', 'id', 'version']},
                           'declaredPermissions': {field: component[field] for field in permission_keys
                                                   if field in component},
                           'enforcementStatus': 'unqualified'})
    return {
        'schemaVersion': '1',
        'kind': 'AdapterInspection',
        'status': 'documentation-only',
        'runtimeQualified': False,
        'executableExportAllowed': False,
        'host': {'id': host, 'version': None, 'versionStatus': 'unobserved'},
        'subject': subject,
        'manifest': manifest,
        'lock': lock,
        'generator': {'sourceRevision': 'content-sha256:' + digest(files), 'files': files,
                      'authenticated': False},
        'declaredPermissions': {key: record[key] for key in permission_keys},
        'componentPermissions': components,
        'adapter': report,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', required=True, help='Exact catalog Agent id, not a file path')
    parser.add_argument('--host', default='codex', help='Inspection host; only codex is documented')
    parser.add_argument('--executable', action='store_true', help='Always rejected; no executable exporter exists')
    args = parser.parse_args(argv)
    try:
        report = inspect_adapter(args.agent, host=args.host, executable=args.executable)
    except (Invalid, OSError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        return 1
    sys.stdout.buffer.write(canonical(report))
    return 0


if __name__ == '__main__':
    sys.exit(main())
