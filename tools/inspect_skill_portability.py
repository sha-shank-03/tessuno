#!/usr/bin/env python3
"""Inspect native Skill format candidates and portability losses offline."""
import argparse
import hashlib
from pathlib import Path
import re
import sys

from library import (ROOT, CONTROLS, Invalid, canonical, component_files, digest,
                     load_catalog, native_skill, read_json, safe_path, subject_manifest)

TOOL_ROOT = Path(__file__).resolve().parents[1]
HOSTS = {'codex', 'claude-code', 'cursor', 'gemini-cli'}
PERMISSION_FIELDS = {'filesystemScope', 'networkScope', 'requiredTools'}


def profiles():
    """Reference data is closed and inert; it is never host configuration."""
    data = read_json(safe_path(TOOL_ROOT, 'tools/skill-host-profiles.json'))
    if (not isinstance(data, dict) or set(data) != {
            'schemaVersion', 'reviewedOn', 'standardReference', 'hosts'} or
            data['schemaVersion'] != '1' or
            not isinstance(data['reviewedOn'], str) or
            not re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['reviewedOn']) or
            data['standardReference'] != 'https://agentskills.io/specification' or
            not isinstance(data['hosts'], dict) or set(data['hosts']) != HOSTS):
        raise Invalid('invalid native Skill documentation profiles')
    for profile in data['hosts'].values():
        if not isinstance(profile, dict) or set(profile) != {
                'documentation', 'projectSkillRoots', 'invocationNote'}:
            raise Invalid('invalid host documentation profile fields')
        if (not isinstance(profile['documentation'], str) or
                not profile['documentation'].startswith('https://') or
                not isinstance(profile['invocationNote'], str) or not profile['invocationNote']):
            raise Invalid('invalid host documentation reference')
        roots = profile['projectSkillRoots']
        if (not isinstance(roots, list) or not roots or
                any(not isinstance(path, str) for path in roots) or len(set(roots)) != len(roots)):
            raise Invalid('invalid project Skill roots')
        for path in roots:
            # Validate reference strings lexically; never inspect real host discovery folders.
            if not re.fullmatch(r'\.(?:agents|claude|cursor|gemini)/skills', path):
                raise Invalid('invalid documented project Skill root')
    return data


def generator_files(root):
    # Bind the actual imported validator and every catalog schema consumed by load_catalog.
    # Reference URLs identify documents, not authenticated snapshots of their remote bytes.
    sources = {
        'tool': (TOOL_ROOT, ['tools/inspect_skill_portability.py',
                            'tools/skill-host-profiles.json', 'requirements-dev.lock']),
        'validator': (ROOT, ['tools/library.py']),
        'catalog': (root, ['schemas/' + name + '.schema.json' for name in
                           ['common', 'agent', 'skill', 'recipe', 'pack', 'evidence']]),
    }
    return [{'source': source, 'path': path,
             'sha256': hashlib.sha256(safe_path(base, path).read_bytes()).hexdigest()}
            for source, (base, paths) in sorted(sources.items()) for path in sorted(paths)]


def body_findings(text):
    # Conservative textual signals, including code examples and escaped tokens.
    # This is not a host parser or an exhaustive safety/portability scan.
    patterns = {
        'claude-dynamic-context': r'!`',
        'claude-substitution': r'\$(?:ARGUMENTS\b|[0-9]+\b|\{CLAUDE_[A-Z_]+\})',
    }
    return [{'signal': signal, 'line': number, 'semantics': 'host-specific-unqualified'}
            for number, line in enumerate(text.splitlines(), 1)
            for signal, pattern in sorted(patterns.items()) if re.search(pattern, line)]


def inspect_skill(skill_id, root=ROOT, host='all', executable=False):
    if not isinstance(skill_id, str):
        raise Invalid('inspection requires an exact catalog Skill id')
    if not isinstance(host, str) or host not in HOSTS | {'all'}:
        raise Invalid('unknown native Skill inspection host')
    if executable:
        raise Invalid('executable export rejected: unsupported controls: ' +
                      ', '.join(CONTROLS) + '; trusted host enforcement unavailable')
    root = Path(root).resolve()
    records = load_catalog(root)
    info = records.get(skill_id)
    if info is None or info['record']['kind'] != 'Skill':
        raise Invalid('inspection requires an exact catalog Skill id')
    record = info['record']
    entry = safe_path(info['path'].parent, record['entry'])
    name = native_skill(entry)
    text = entry.read_text(encoding='utf-8')
    # SKILL.md is not reconstructed from sidecar title/purpose or host fields.
    # No field value is flattened, injected, renamed or treated as enforcement.
    losses = []
    for field, value in sorted(record.items()):
        status = ('native-entrypoint' if field == 'entry' else
                  'unsupported-enforcement' if field in PERMISSION_FIELDS else
                  'report-only-no-native-mapping')
        losses.append({'field': field, 'value': value, 'status': status,
                       'nativeField': 'SKILL.md' if field == 'entry' else None})
    files = component_files(root, info)
    sidecar = info['path'].relative_to(root).as_posix()
    inventory = [{**item,
                  'relativePath': safe_path(root, item['path']).relative_to(entry.parent).as_posix(),
                  'role': 'canonical-sidecar' if item['path'] == sidecar else
                          'native-entrypoint' if item['path'] == entry.relative_to(root).as_posix() else
                          'resource-unqualified'} for item in files]
    references = profiles()
    selected = sorted(HOSTS) if host == 'all' else [host]
    candidates = [{
        'id': key, 'version': None, 'versionStatus': 'unobserved',
        'status': 'documentation-only', 'runtimeQualified': False,
        'inspectedFrontmatterSubset': ['name', 'description'],
        'suggestedProjectDirectories': [path + '/' + name for path in
                                       references['hosts'][key]['projectSkillRoots']],
        'reference': references['hosts'][key],
        'documentedNameLosses': ['reserved-name-not-discovered'] if key == 'claude-code' and
                               name in {'synced', 'anthropic-skills'} else [],
        'nativeBehavior': 'unqualified', 'resourceResolution': 'unqualified',
        'toolMappings': {tool: 'unqualified' for tool in record['requiredTools']},
        'unsupportedControls': list(CONTROLS),
    } for key in selected]
    subject, manifest, lock, _ = subject_manifest(root, records, skill_id)
    generator = generator_files(root)
    report = {
        'schemaVersion': '1', 'kind': 'NativeSkillPortabilityInspection',
        'status': 'documentation-only', 'runtimeQualified': False,
        'executableExportAllowed': False,
        'subject': subject, 'manifest': manifest, 'lock': lock,
        'generator': {'sourceRevision': 'content-sha256:' + digest(generator),
                      'files': generator, 'authenticated': False,
                      'installedDependenciesVerified': False},
        'documentationProfiles': references, 'profileDigest': digest(references),
        'remoteDocumentationAuthenticated': False,
        'native': {'name': name, 'entry': entry.relative_to(root).as_posix(),
                   'rewritePerformed': False, 'files': inventory,
                   'bodySignals': body_findings(text), 'signalsAreExhaustive': False},
        'canonicalFields': losses, 'hosts': candidates,
        'limitations': [
            'Source and resources are inventoried, not copied or installed.',
            'Native format and byte preservation do not establish equivalent host behavior.',
            'Sidecar permissions and prompt instructions are not enforced host policy.',
            'Skills have no requiredControls field; controls listed here are unqualified inspection checks.',
            'Host versions and resource resolution are unobserved; no host smoke test ran.',
        ],
    }
    return {**report, 'reportDigest': digest(report)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill', required=True, help='Exact catalog Skill id')
    parser.add_argument('--host', default='all', help='all, codex, claude-code, cursor or gemini-cli')
    parser.add_argument('--executable', action='store_true', help='Always rejected')
    args = parser.parse_args(argv)
    try:
        report = inspect_skill(args.skill, host=args.host, executable=args.executable)
    except (Invalid, OSError, UnicodeError, TypeError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        return 1
    sys.stdout.buffer.write(canonical(report))
    return 0


if __name__ == '__main__':
    sys.exit(main())
