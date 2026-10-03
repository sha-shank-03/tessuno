"""Offline contract and catalog foundation. This module never executes library objects."""
from __future__ import annotations
import hashlib, json, re
import yaml
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CONTROLS = ['filesystem-scope', 'network-scope', 'human-approval-gates']
KINDS = {'Agent': ('agents', 'agent.json'), 'Skill': ('skills', 'library.json'), 'Recipe': ('recipes', 'recipe.json'), 'Pack': ('packs', 'pack.json')}
class Invalid(ValueError): pass

def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)+'\n').encode()
def digest(value): return hashlib.sha256(canonical(value)).hexdigest()
def no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out: raise Invalid(f'duplicate JSON key: {key}')
        out[key] = value
    return out
def read_json(path):
    try: return json.loads(Path(path).read_text(), object_pairs_hook=no_duplicates)
    except (ValueError, OSError) as exc: raise Invalid(str(exc)) from exc

def safe_path(root, value, must_exist=True):
    if not isinstance(value, str) or not value or '\\' in value or '\x00' in value:
        raise Invalid('invalid relative path')
    parts = value.split('/')
    if any(p in ('', '.', '..') for p in parts) or PurePosixPath(value).is_absolute() or ':' in value:
        raise Invalid(f'unsafe path: {value}')
    root = Path(root).resolve()
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink(): raise Invalid(f'symlink forbidden: {value}')
    if not current.resolve().is_relative_to(root): raise Invalid('path escapes root')
    if must_exist and not current.is_file(): raise Invalid(f'missing file: {value}')
    return current

def checked_schema(root, name):
    schema = read_json(safe_path(root, 'schemas/'+name+'.schema.json'))
    def local_refs(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in ('$ref','$dynamicRef','$recursiveRef') and (not isinstance(item,str) or not item.startswith('#/')):
                    raise Invalid('nonlocal schema reference forbidden')
                local_refs(item)
        elif isinstance(value,list):
            for item in value: local_refs(item)
    local_refs(schema)
    Draft202012Validator.check_schema(schema)
    return schema

def validate_schema(record, schema_name=None, root=ROOT):
    name = schema_name or record.get('kind', '').lower()
    if name not in ('agent','skill','recipe','pack','evidence'): raise Invalid('unknown record kind')
    schema = checked_schema(root,name)
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record), key=lambda e: str(e.path))
    if errors: raise Invalid('; '.join(f'{list(e.path)}: {e.message}' for e in errors))

def scope_check(record):
    for mode, paths in record.get('filesystemScope', {}).items():
        for value in paths:
            prefix = '${workspace}/'
            if not value.startswith(prefix): raise Invalid('scope must be workspace-relative')
            safe_path(ROOT, value[len(prefix):], must_exist=False)
    net = record.get('networkScope')
    if net and net['mode'] == 'allowlist':
        if not net['destinations']: raise Invalid('empty network allowlist')
        for host in net['destinations']:
            if not re.fullmatch(r'[a-z0-9]+(?:[.-][a-z0-9]+)*', host): raise Invalid('destination must be an exact lowercase hostname')
    if set(record.get('requiredTools', [])) - {'repository.read'}:
        raise Invalid('unsupported tool capability')

def native_skill(path):
    text = path.read_text()
    if not text.startswith('---\n') or '\n---\n' not in text[4:]:
        raise Invalid('missing native Skill frontmatter')
    front, body = text[4:].split('\n---\n', 1)
    class StrictLoader(yaml.SafeLoader):
        pass
    def mapping(loader, node, deep=False):
        pairs = loader.construct_pairs(node, deep=deep)
        try: return no_duplicates(pairs)
        except (TypeError, ValueError) as exc: raise Invalid('invalid or duplicate native frontmatter key') from exc
    StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try: data = yaml.load(front, Loader=StrictLoader)
    except yaml.YAMLError as exc: raise Invalid('invalid native Skill YAML') from exc
    if not isinstance(data, dict) or set(data) != {'name', 'description'}:
        raise Invalid('supported native frontmatter requires exactly name and description')
    name, description = data['name'], data['description']
    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or name != path.parent.name or len(name)>64:
        raise Invalid('invalid native Skill name')
    if not isinstance(description, str) or not description.strip() or len(description)>1024 or not body.strip():
        raise Invalid('native description and body must be nonempty strings')
    return name

def references(record):
    return record.get('skills', []) + [s['uses'] for s in record.get('steps', [])] + record.get('members', [])
def load_catalog(root=ROOT):
    root = Path(root).resolve(); records = {}
    # Every consumed schema and static asset is checked before any consumer reads it.
    for name in ['common','agent','skill','recipe','pack','evidence']:
        checked_schema(root,name)
    for asset in ['site/assets/style.css','site/assets/search.js','LICENSE','THIRD_PARTY_NOTICES.md']: safe_path(root,asset)

    for kind, (directory, filename) in KINDS.items():
        folder = root/directory
        if folder.is_symlink(): raise Invalid('catalog directory is a symlink')
        for path in sorted(folder.glob('*/'+filename)):
            safe_path(root, path.relative_to(root).as_posix())
            item = read_json(path); validate_schema(item, root=root)
            if item['kind'] != kind: raise Invalid('kind/directory mismatch')
            if item['id'] in records: raise Invalid('duplicate object id')
            scope_check(item)
            if kind == 'Agent': safe_path(path.parent, item['instructions'])
            if kind == 'Skill': native_skill(safe_path(path.parent, item['entry']))
            ids = [x['id'] for x in item.get('steps', [])]
            if len(ids) != len(set(ids)): raise Invalid('duplicate recipe step id')
            for support in item.get('supportedPlatforms', []):
                if support['declaredIntent'] == 'supported': raise Invalid('qualified support claims unavailable in v0')
            records[item['id']] = {'record':item, 'path':path}
    if not records: raise Invalid('empty catalog')
    for info in records.values(): component_files(root, info)
    for info in records.values():
        for ref in references(info['record']):
            target = records.get(ref['id'], {}).get('record')
            if not target or any(target[k] != ref[k] for k in ('kind','id','version')): raise Invalid('unresolved exact reference')
    def visit(id, active):
        if id in active: raise Invalid('dependency cycle')
        for ref in references(records[id]['record']): visit(ref['id'], active|{id})
    for id in records: visit(id,set())
    return records

def closure(records, id):
    seen = set()
    def visit(key):
        if key in seen:return
        seen.add(key)
        for ref in references(records[key]['record']):visit(ref['id'])
    visit(id);return sorted(seen)

def component_files(root, info):
    root=Path(root).resolve();files=[]
    for path in sorted(info['path'].parent.rglob('*')):
        if path.is_symlink():raise Invalid('symlink in component closure')
        if not path.is_dir() and not path.is_file(): raise Invalid('nonregular component resource')
        if path.is_file():
            relative=path.relative_to(root).as_posix();safe_path(root,relative)
            if path.suffix not in {'.json','.md','.txt'}:raise Invalid('unreviewed component file type')
            files.append({'path':relative,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    return files

def adapter_report(record):
    """Loss report only. No executable host files or runtime claims are emitted."""
    validate_schema(record)
    if record['kind']!='Agent':raise Invalid('adapter requires Agent')
    return {'schemaVersion':'1','host':'codex','status':'documentation-only','runtimeQualified':False,
            'subjectId':record['id'],'preserved':['name/purpose','instructions'],
            'transformed':[], 'unsupported':list(record['requiredControls']),
            'toolMappings':{'repository.read':'unqualified'},
            'reason':'No host enforcement or approval-gate tests have run. Generation is blocked for executable use.'}

def qualify(record, report):
    validate_schema(record)
    # No trusted runtime verifier exists in this foundation; caller-provided reports cannot grant authority.
    raise Invalid('executable qualification unavailable: trusted host enforcement verification is not implemented')

def subject_manifest(root, records, id):
    root=Path(root).resolve();components=[];files=[]
    for key in closure(records,id):
        info=records[key];part=component_files(root,info);files+=part
        components.append({'id':key,'version':info['record']['version'],'sha256':digest(part)})
    adapters=[adapter_report(records[key]['record']) for key in closure(records,id) if records[key]['record']['kind']=='Agent']
    adapter_digest=digest(adapters)
    lock={'schemaVersion':'1','components':components,'adapterDigest':adapter_digest,'licenses':[{'id':key,'license':records[key]['record']['license']} for key in closure(records,id)]}
    # Bind applicable license/attribution bytes as part of each candidate, outside component IDs.
    for relative in ['LICENSE','THIRD_PARTY_NOTICES.md']:
        files.append({'path':relative,'sha256':hashlib.sha256(safe_path(root,relative).read_bytes()).hexdigest()})
    # A content snapshot is used instead of a mutable branch or a self-referential Git commit.
    revision='content-sha256:'+digest(sorted(files,key=lambda x:x['path']))
    manifest={'sourceRevision':revision,'files':sorted(files,key=lambda x:x['path']),'components':components,'adapterDigest':adapter_digest,'lockDigest':digest(lock)}
    subject={'id':id,'version':records[id]['record']['version'],'sha256':digest(manifest),**{k:manifest[k] for k in ['sourceRevision','components','adapterDigest','lockDigest']}}
    return subject,manifest,lock,adapters

def evidence_check(record, expected_subject=None, scope_digest=None, expected_attempts=None, now=None):
    validate_schema(record,'evidence')
    subject=record['subject'];details=record['details'];category=record['category']
    components=[x['id'] for x in subject['components']]
    if len(components)!=len(set(components)):raise Invalid('duplicate evidence component')
    if expected_subject is not None and subject != expected_subject:raise Invalid('stale or mismatched subject digest/closure')
    if category=='human-review':
        if details['candidateDigest']!=subject['sha256']:raise Invalid('stale approval digest')
        if scope_digest is not None and details['scopeDigest']!=scope_digest:raise Invalid('stale approval scope')
    if category=='execution':
        attempts=details['attempts'];ids=[a['id'] for a in attempts]
        if len(ids)!=len(set(ids)):raise Invalid('duplicate attempt ids')
        for a in attempts:
            if a['assertionsPassed']+a['assertionsFailed'] != a['assertionsExecuted']:raise Invalid('inconsistent assertion counts')
            if a['status']=='pass' and (a['assertionsExecuted']==0 or a['assertionsFailed']):raise Invalid('invalid attempt pass')
        if expected_attempts is not None and {a['id']:a['assertionsExecuted'] for a in attempts}!=expected_attempts:raise Invalid('predeclared attempt/assertion completeness mismatch')
    if category=='compatibility':
        ids=[x['id'] for x in details['testCases']]
        if len(ids)!=len(set(ids)):raise Invalid('duplicate compatibility case')
    if category=='security':
        now=now or datetime.now(timezone.utc)
        for s in details['suppressions']:
            if datetime.fromisoformat(s['expiresAt'].replace('Z','+00:00'))<=now:raise Invalid('expired suppression')
    return True

def trust_evidence(record, **kwargs):
    evidence_check(record, **kwargs)
    raise Invalid('producer provenance verification unavailable; structurally valid evidence is untrusted')

def publication_gate(records):
    # Full SPDX expression/file policy, identities, provenance and host qualification are future gates.
    raise Invalid('publication blocked: public identity, release policy and trusted qualification gates are unresolved')
