#!/usr/bin/env python3
"""Generate an inert source-inspection catalog and deterministic archive; never publish or install."""
from pathlib import Path
import html,json,posixpath,zipfile
from urllib.parse import quote
from library import ROOT,load_catalog,subject_manifest,canonical,digest,Invalid,safe_path,read_json,closure

def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_bytes(data if isinstance(data,bytes) else data.encode())
def object_anchor(id):
 return 'object-'+id
def object_link(id):
 return '#'+quote(object_anchor(id),safe='')
def source_page(path,data,dest,raw,objects=()):
 base=posixpath.dirname(dest) or '.'
 def url(target):return html.escape(quote(posixpath.relpath(target,base),safe='/'),quote=True)
 sha=__import__('hashlib').sha256(data).hexdigest()
 context=''
 if objects:
  links=''.join('<li><a href="'+url('index.html')+object_link(id)+'">'+html.escape(title)+'</a> · <code>'+html.escape(id)+'</code></li>' for id,title in objects)
  context='<section aria-label="Objects including this source"><h2>Objects including this source</h2><p>These catalog objects include this file in their exact dependency closure.</p><ul>'+links+'</ul></section>'
 try:preview='<pre id="source-text"><code>'+html.escape(data.decode('utf-8'))+'</code></pre>'
 except UnicodeDecodeError:preview='<p>UTF-8 text preview unavailable for this file. The raw file retains the original bytes.</p>'
 return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; base-uri 'none'; form-action 'none'"><title>'''+html.escape(path)+''' · Tessuno source</title><link rel="stylesheet" href="'''+url('style.css')+'''"></head><body><main class="source-viewer"><nav aria-label="Source navigation"><a href="'''+url('index.html')+'''">Catalog</a> · <a href="'''+url(raw)+'''">Raw bytes</a> · <a href="https://github.com/sha-shank-03/tessuno">Repository</a></nav><header><p class="eyebrow">TESSUNO / SOURCE INSPECTION</p><h1>Inspect source.</h1><p class="source-path"><code>'''+html.escape(path)+'''</code></p><p class="notice">Source text is displayed as data. This page does not run source instructions or establish runtime qualification.</p><p>Original file: '''+str(len(data))+''' bytes · SHA256 <code>'''+sha+'''</code></p></header>'''+context+preview+'''</main></body></html>'''
def declared_controls(records,id):
 keys=['filesystemScope','networkScope','requiredTools','humanApprovalRequirements','requiredControls']
 components=[]
 for key in closure(records,id):
  item=records[key]['record']
  components.append({**{field:item[field] for field in ['kind','id','version']},'declaredPermissions':{field:item[field] for field in keys if field in item}})
 return {'basis':'exact-dependency-closure','enforcementStatus':'unqualified','components':components}
def build(out=None):
 root=Path(ROOT).resolve();records=load_catalog();out=out or root/'dist'
 previous={}
 if out.exists():
  if out.is_symlink() or out.resolve()!=root/'dist':raise Invalid('unsafe output directory')
  # Only overwrite or remove unchanged outputs named in the prior generated receipt.
  receipt=safe_path(out,'checksums.json')
  if not receipt.is_file(): raise Invalid('existing output lacks generated receipt')
  previous=read_json(receipt)
  if not isinstance(previous,dict): raise Invalid('invalid generated receipt')
  for name,sha in previous.items():
   path=safe_path(out,name)
   if __import__('hashlib').sha256(path.read_bytes()).hexdigest()!=sha: raise Invalid('modified generated output; refusing overwrite')
  for p in out.rglob('*'):
   if p.is_symlink():raise Invalid('symlink in output')
   if p.is_file() and p.relative_to(out).as_posix() not in set(previous)|{'checksums.json'}:
    raise Invalid('unowned output file; refusing overwrite or cleanup')
 out.mkdir(exist_ok=True)
 cards=[];index=[];bundle={};viewers=set();source_objects={}
 for id,info in sorted(records.items()):
  item=info['record'];subject,manifest,lock,adapters=subject_manifest(root,records,id)
  bundle[id]={'subject':subject,'manifest':manifest,'lock':lock,'adapters':adapters}
  controls=declared_controls(records,id);permissions=[component['declaredPermissions'] for component in controls['components']]
  fields={'kind':item['kind'],'stack':' '.join(item['stacks']),'platform':' '.join(x['host'] for x in item.get('supportedPlatforms',[])) or 'unqualified','origin':'original-synthetic','support':'declared-only','network':'allowlist' if any(p.get('networkScope',{}).get('mode')=='allowlist' for p in permissions) else 'none','write':'declared' if any(p.get('filesystemScope',{}).get('write') for p in permissions) else 'none'}
  index.append({'id':id,'title':item['title'],'purpose':item['purpose'],**fields,'declaredControls':controls,'sha256':subject['sha256']})
  source=info['path'].relative_to(root).as_posix()
  sources=[]
  for entry in manifest['files']:
   path=entry['path'];raw='source/'+path+'.txt';dest='source/'+path+'.html';data=safe_path(root,path).read_bytes()
   write(out/raw,data);source_objects.setdefault(path,[]).append((id,item['title']));viewers.add(dest)
   sources.append(f'<li><a href="{html.escape(quote(dest,safe="/"),quote=True)}">{html.escape(path)}</a> (<a href="{html.escape(quote(raw,safe="/"),quote=True)}">Raw bytes</a>)</li>')
  search=' '.join([id,item['title'],item['purpose'],*fields.values(),'network:'+fields['network'],'write:'+fields['write']])
  scope=f'<p>Declared scope summary across the exact dependency closure: network: {fields["network"]}; write: {fields["write"]}. Component declarations imply no enforcement or combined permission policy.</p><details><summary>Inspect declared controls across dependencies</summary><pre>'+html.escape(json.dumps(controls,indent=2))+'</pre></details>'
  direct='<a href="'+quote('source/'+source+'.html',safe='/')+'">Inspect contract source</a>'
  if item['kind']=='Skill':
   entry=safe_path(info['path'].parent,item['entry']).relative_to(root).as_posix()
   direct+=' · <a href="'+quote('source/'+entry+'.html',safe='/')+'">Inspect native SKILL.md</a>'
  navigation='<p class="object-id"><a href="'+object_link(id)+'" aria-label="'+html.escape('Link to '+id,quote=True)+'"><code>'+html.escape(id)+'</code></a></p><p>'+direct+'</p>'
  cards.append('<article id="'+html.escape(object_anchor(id),quote=True)+'" tabindex="-1" data-kind="'+html.escape(item['kind'],quote=True)+'" data-stacks="'+html.escape(json.dumps(item['stacks']),quote=True)+'" data-search="'+html.escape(search,quote=True)+'">'+f'<p class="eyebrow">{html.escape(item["kind"])} · v{item["version"]}</p><h2>{html.escape(item["title"])}</h2>'+navigation+f'<p>{html.escape(item["purpose"])}</p><p class="status">Declared-only · no runtime qualification · license {html.escape(item["license"])}</p><p>Validation: local structural checks only. Security scan, independent review, host execution, and enforcement: no trusted evidence.</p>'+scope+f'<p>Exact content digest: <code>{subject["sha256"]}</code></p><details><summary>Inspect full contract</summary><pre>'+html.escape(json.dumps(item,indent=2))+'</pre></details><details><summary>Inspect source and dependency closure</summary><ul>'+''.join(sources)+'</ul></details></article>')
 for path,objects in sorted(source_objects.items()):
  raw='source/'+path+'.txt';dest='source/'+path+'.html'
  write(out/dest,source_page(path,(out/raw).read_bytes(),dest,raw,objects))
 kinds=sorted({info['record']['kind'] for info in records.values()})
 stacks=sorted({stack for info in records.values() for stack in info['record']['stacks']})
 def options(values):
  return ''.join('<option value="'+html.escape(value,quote=True)+'">'+html.escape(value)+'</option>' for value in values)
 filters='<div class="filters"><div><label for="kind">Object type</label><select id="kind" disabled><option value="">All types</option>'+options(kinds)+'</select></div><div><label for="stack">Stack</label><select id="stack" disabled><option value="">All stacks</option>'+options(stacks)+'</select></div></div><button id="reset" type="button" disabled>Clear search and filters</button><p id="empty" hidden>No objects match. Try fewer search terms or clear the filters.</p>'
 write(out/'search-index.json',canonical(index));write(out/'content-manifests.json',canonical(bundle))
 for name in ['content-manifests','search-index']:
  dest=name+'.html';write(out/dest,source_page(name+'.json',(out/(name+'.json')).read_bytes(),dest,name+'.json'));viewers.add(dest)
 css=safe_path(root,'site/assets/style.css').read_text();js=safe_path(root,'site/assets/search.js').read_text()
 write(out/'style.css',css);write(out/'search.js',js)
 page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; base-uri 'none'; form-action 'none'"><title>Tessuno · development catalog</title><link rel="stylesheet" href="style.css"></head><body><main><header><p class="eyebrow">TESSUNO / DEVELOPMENT FOUNDATION / v0.1</p><h1>Tessuno.<br>Inspectable capabilities.</h1><p>Original synthetic objects for bounded iOS review, build-diagnosis and release-evidence workflows.</p><p class="notice">Source inspection preview. Original work: Apache-2.0. Maintainer: sha-shank-03. Compatibility is declared-only; no authenticated runtime evidence or security qualification. Nothing here installs, executes, or qualifies a host.</p></header><section class="search"><label for="search">Search type, stack, platform, origin, support, network or write scope</label><input id="search" type="search" placeholder="Try Skill, ios, codex, declared-only, none" disabled>'''+filters+'''<p id="count" role="status">4 objects</p><noscript>All objects and source links are available below without JavaScript.</noscript></section>'''+''.join(cards)+'''<footer><p>No trusted evidence is imported. Valid evidence syntax never awards a badge.</p><p><a href="content-manifests.html">Content manifests and exact locks</a> · <a href="search-index.html">Search index</a> · <a href="prototype.zip">Synthetic source archive</a></p></footer></main><script src="search.js"></script></body></html>'''
 write(out/'index.html',page.replace('<p id="count" role="status">4 objects</p>',f'<p id="count" role="status">{len(records)} objects</p>'))
 archive_files={}
 for info in records.values():
  for p in info['path'].parent.rglob('*'):
   if p.is_file():archive_files[p.relative_to(root).as_posix()]=safe_path(root,p.relative_to(root).as_posix()).read_bytes()
 for p in sorted((root/'schemas').glob('*.json')):archive_files[p.relative_to(root).as_posix()]=safe_path(root,p.relative_to(root).as_posix()).read_bytes()
 archive_files['content-manifests.json']=canonical(bundle)
 archive_files['LICENSE']=safe_path(root,'LICENSE').read_bytes()
 archive_files['THIRD_PARTY_NOTICES.md']=safe_path(root,'THIRD_PARTY_NOTICES.md').read_bytes()
 archive_files['LICENSE-STATUS.txt']=b'Apache-2.0 for original scaffold work. See LICENSE and THIRD_PARTY_NOTICES.md. Inspectable source availability grants no executable qualification or verified-release authority.\n'
 with zipfile.ZipFile(out/'prototype.zip','w',compression=zipfile.ZIP_STORED) as z:
  for path,data in sorted(archive_files.items()):
   zi=zipfile.ZipInfo(path,(1980,1,1,0,0,0));zi.external_attr=0o100644<<16;zi.create_system=3;z.writestr(zi,data)
 generated=['index.html','style.css','search.js','search-index.json','content-manifests.json','prototype.zip']+sorted(viewers)+['source/'+e['path']+'.txt' for b in bundle.values() for e in b['manifest']['files']]
 checks={p:__import__('hashlib').sha256((out/p).read_bytes()).hexdigest() for p in sorted(set(generated))}
 for stale in sorted(set(previous)-set(checks)):
  safe_path(out,stale).unlink()  # Only prior generated bytes verified unchanged above.
 write(out/'checksums.json',canonical(checks));print(f'Built {len(records)} objects, {len(checks)} outputs; root digest {digest(checks)}')
 return checks
if __name__=='__main__':build()
