#!/usr/bin/env python3
"""Generate an inert source-inspection catalog and deterministic archive; never publish or install."""
from pathlib import Path
import html,json,zipfile
from urllib.parse import quote
from library import ROOT,load_catalog,subject_manifest,canonical,digest,Invalid,safe_path,read_json

def write(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_bytes(data if isinstance(data,bytes) else data.encode())
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
 cards=[];index=[];bundle={}
 for id,info in sorted(records.items()):
  item=info['record'];slug=id.replace('/','--');subject,manifest,lock,adapters=subject_manifest(root,records,id)
  bundle[id]={'subject':subject,'manifest':manifest,'lock':lock,'adapters':adapters}
  fields={'kind':item['kind'],'stack':' '.join(item['stacks']),'platform':' '.join(x['host'] for x in item.get('supportedPlatforms',[])) or 'unqualified','origin':'original-synthetic','support':'declared-only','network':item.get('networkScope',{}).get('mode','composed'),'write':'none' if not item.get('filesystemScope',{}).get('write') else 'declared'}
  index.append({'id':id,'title':item['title'],'purpose':item['purpose'],**fields,'sha256':subject['sha256']})
  source=info['path'].relative_to(root).as_posix()
  sources=[]
  for entry in manifest['files']:
   path=entry['path'];dest='source/'+path+'.txt';write(out/dest,safe_path(root,path).read_bytes());sources.append(f'<li><a href="{html.escape(quote(dest,safe="/"),quote=True)}">{html.escape(path)}</a></li>')
  cards.append('<article data-kind="'+html.escape(item['kind'],quote=True)+'" data-stacks="'+html.escape(json.dumps(item['stacks']),quote=True)+'" data-search="'+html.escape(' '.join([id,item['title'],item['purpose'],*fields.values()]),quote=True)+'">'+f'<p class="eyebrow">{html.escape(item["kind"])} · v{item["version"]}</p><h2>{html.escape(item["title"])}</h2><p>{html.escape(item["purpose"])}</p><p class="status">Declared-only · no runtime qualification · license {html.escape(item["license"])}</p><p>Validation: local structural checks only. Security scan, independent review, host execution, and enforcement: no trusted evidence.</p><p>Exact content digest: <code>{subject["sha256"]}</code></p><details><summary>Inspect full contract</summary><pre>'+html.escape(json.dumps(item,indent=2))+'</pre></details><details><summary>Inspect source and dependency closure</summary><ul>'+''.join(sources)+'</ul></details></article>')
 kinds=sorted({info['record']['kind'] for info in records.values()})
 stacks=sorted({stack for info in records.values() for stack in info['record']['stacks']})
 def options(values):
  return ''.join('<option value="'+html.escape(value,quote=True)+'">'+html.escape(value)+'</option>' for value in values)
 filters='<div class="filters"><div><label for="kind">Object type</label><select id="kind" disabled><option value="">All types</option>'+options(kinds)+'</select></div><div><label for="stack">Stack</label><select id="stack" disabled><option value="">All stacks</option>'+options(stacks)+'</select></div></div><button id="reset" type="button" disabled>Clear search and filters</button><p id="empty" hidden>No objects match. Try fewer search terms or clear the filters.</p>'
 write(out/'search-index.json',canonical(index));write(out/'content-manifests.json',canonical(bundle))
 css=safe_path(root,'site/assets/style.css').read_text();js=safe_path(root,'site/assets/search.js').read_text()
 write(out/'style.css',css);write(out/'search.js',js)
 page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self'; base-uri 'none'; form-action 'none'"><title>Tessuno · development catalog</title><link rel="stylesheet" href="style.css"></head><body><main><header><p class="eyebrow">TESSUNO / DEVELOPMENT FOUNDATION / v0.1</p><h1>Tessuno.<br>Inspectable capabilities.</h1><p>Original synthetic objects for bounded iOS review, build-diagnosis and release-evidence workflows.</p><p class="notice">Source inspection preview. Original work: Apache-2.0. Maintainer: sha-shank-03. Compatibility is declared-only; no authenticated runtime evidence or security qualification. Nothing here installs, executes, or qualifies a host.</p></header><section class="search"><label for="search">Search type, stack, platform, origin, support, network or write scope</label><input id="search" type="search" placeholder="Try Skill, ios, codex, declared-only, none" disabled>'''+filters+'''<p id="count" role="status">4 objects</p><noscript>All objects and source links are available below without JavaScript.</noscript></section>'''+''.join(cards)+'''<footer><p>No trusted evidence is imported. Valid evidence syntax never awards a badge.</p><p><a href="content-manifests.json">Content manifests and exact locks</a> · <a href="search-index.json">Search index</a> · <a href="prototype.zip">Synthetic source archive</a></p></footer></main><script src="search.js"></script></body></html>'''
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
 generated=['index.html','style.css','search.js','search-index.json','content-manifests.json','prototype.zip']+['source/'+e['path']+'.txt' for b in bundle.values() for e in b['manifest']['files']]
 checks={p:__import__('hashlib').sha256((out/p).read_bytes()).hexdigest() for p in sorted(set(generated))}
 for stale in sorted(set(previous)-set(checks)):
  safe_path(out,stale).unlink()  # Only prior generated bytes verified unchanged above.
 write(out/'checksums.json',canonical(checks));print(f'Built {len(records)} objects, {len(checks)} outputs; root digest {digest(checks)}')
 return checks
if __name__=='__main__':build()
