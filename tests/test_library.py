import copy,hashlib,json,sys,tempfile,unittest,zipfile,shutil
from unittest.mock import patch
from urllib.parse import unquote
from html.parser import HTMLParser
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from library import *
from build import build
class Contracts(unittest.TestCase):
 def evidence(self,category):return read_json(ROOT/f'tests/fixtures/valid/evidence-{category}.json')
 def test_schemas_valid(self):
  for p in (ROOT/'schemas').glob('*.json'):Draft202012Validator.check_schema(read_json(p))
 def test_original_and_build_diagnosis_objects(self):
  records=load_catalog();self.assertEqual(len(records),10)
  self.assertEqual(records['core/xcode-build-diagnostician']['record']['kind'],'Agent')
  self.assertEqual(records['core/xcode-build-diagnosis']['record']['kind'],'Skill')
 def test_original_and_release_objects(self):
  records=load_catalog();self.assertEqual(len(records),10)
  self.assertEqual(records['core/release-readiness-evidence']['record']['kind'],'Skill')
 def test_root_alias_preserves_digests_builds_and_symlink_rejection(self):
  import build as builder
  with tempfile.TemporaryDirectory() as d:
   parent=Path(d).resolve();root=parent/'repo'
   shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','dist','__pycache__'))
   alias=parent/'alias';alias.symlink_to(root,target_is_directory=True)
   expected=subject_manifest(root,load_catalog(root),'core/ios-studio')
   self.assertEqual(subject_manifest(alias,load_catalog(alias),'core/ios-studio'),expected)
   records=load_catalog(alias);info=records['core/ios-studio']
   self.assertEqual(component_files(alias,info),component_files(root,info))
   with patch.object(builder,'ROOT',alias),patch.object(builder,'load_catalog',lambda:load_catalog(alias)):
    self.assertEqual(builder.build(),builder.build())
   outside=parent/'outside.md';outside.write_text('outside fixture')
   target=root/'skills/ios-test-plan/examples/toggle.md';target.unlink();target.symlink_to(outside)
   with self.assertRaises(Invalid):load_catalog(alias)
   with self.assertRaises(Invalid):subject_manifest(alias,records,'core/ios-studio')
 def test_positive_fixtures(self):
  for p in (ROOT/'tests/fixtures/valid').glob('*.json'):
   with self.subTest(p=p.name):
    r=read_json(p);evidence_check(r) if 'category' in r else validate_schema(r)
 def test_negative_fixtures(self):
  for p in (ROOT/'tests/fixtures/invalid').glob('*.json'):
   with self.subTest(p=p.name),self.assertRaises(Invalid):validate_schema(read_json(p))
 def test_required_agent_fields(self):
  a=read_json(ROOT/'agents/ios-quality-reviewer/agent.json')
  for key in a:
   b=copy.deepcopy(a);del b[key]
   with self.subTest(key=key),self.assertRaises(Invalid):validate_schema(b)
 def test_closed_nested_records(self):
  a=read_json(ROOT/'agents/ios-quality-reviewer/agent.json')
  for key in ['maintainer','networkScope','filesystemScope','activation']:
   b=copy.deepcopy(a);b[key]['hidden']=True
   with self.subTest(key=key),self.assertRaises(Invalid):validate_schema(b)
 def test_exact_references(self):
  for version in ['latest','^0.1.0','0.1','01.1.0']:
   a=read_json(ROOT/'agents/ios-quality-reviewer/agent.json');a['skills'][0]['version']=version
   with self.subTest(version=version),self.assertRaises(Invalid):validate_schema(a)
 def test_network_none(self):
  a=read_json(ROOT/'agents/ios-quality-reviewer/agent.json');a['networkScope']['destinations']=['example.invalid']
  with self.assertRaises(Invalid):validate_schema(a)
 def test_scope_traversal(self):
  for path in ['../private','${workspace}/../private','/etc/passwd','${workspace}/a/../../b','${workspace}/a\\b']:
   with self.subTest(path=path),self.assertRaises(Invalid):scope_check({'filesystemScope':{'read':[path]}})
 def test_unsafe_paths(self):
  for path in ['../x','/etc/passwd','a/../x','a//x','./x','x\\y','https://x']:
   with self.subTest(path=path),self.assertRaises(Invalid):safe_path(ROOT,path,False)
 def test_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'link').symlink_to('/tmp')
   with self.assertRaises(Invalid):safe_path(p,'link/anything',False)
 def test_duplicate_json(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a.json';p.write_text('{"id":1,"id":2}')
   with self.assertRaises(Invalid):read_json(p)
 def test_pass_invariants(self):
  variants=[]
  e=self.evidence('execution');e['details']['attempts']=[];variants.append(e)
  for status in ['timeout','fail','error','not-run','blocked','skipped']:
   e=self.evidence('execution');e['details']['attempts'][0]['status']=status;variants.append(e)
  e=self.evidence('execution');e['details']['attempts'][0]['assertionsExecuted']=0;variants.append(e)
  e=self.evidence('execution');e['details']['attempts'][0]['assertionsPassed']=0;variants.append(e)
  e=self.evidence('execution');e['details']['attempts']*=2;variants.append(e)
  e=self.evidence('compatibility');e['details']['testCases'][0]['status']='not-run';variants.append(e)
  e=self.evidence('enforcement');e['details']['controls'][0]['coverage']='partial';variants.append(e)
  e=self.evidence('enforcement');e['details']['controls'][0]['control']='network-scope';variants.append(e)
  e=self.evidence('security');e['details']['outcome']='scan_error';variants.append(e)
  e=self.evidence('security');del e['details']['scannerVersion'];variants.append(e)
  e=self.evidence('human-review');e['details']['candidateDigest']='f'*64;variants.append(e)
  e=self.evidence('human-review');e['details']['decision']='reject';variants.append(e)
  e=self.evidence('structure');e['producer']=self.evidence('human-review')['producer'];variants.append(e)
  e=self.evidence('structure');e['details']['scanner']='unexpected';variants.append(e)
  for i,e in enumerate(variants):
   with self.subTest(case=i),self.assertRaises(Invalid):evidence_check(e)
 def test_stale_scope(self):
  with self.assertRaises(Invalid):evidence_check(self.evidence('human-review'),scope_digest='f'*64)
 def test_assertion_completeness(self):
  with self.assertRaises(Invalid):evidence_check(self.evidence('execution'),expected_attempts={'case-1':2})
 def test_no_self_awarded_trust(self):
  for category in ['structure','security','compatibility','execution','enforcement','human-review']:
   with self.subTest(category=category),self.assertRaises(Invalid):trust_evidence(self.evidence(category))
 def test_no_executable_adapter(self):
  a=read_json(ROOT/'agents/ios-quality-reviewer/agent.json');r=adapter_report(a)
  self.assertFalse(r['runtimeQualified']);self.assertEqual(set(r['unsupported']),set(CONTROLS))
  for forged in [r,{'runtimeQualified':True,'unsupported':[]}]:
   with self.assertRaises(Invalid):qualify(a,forged)
 def test_transitive_digest_and_staleness(self):
  r=load_catalog();s,manifest,lock,_=subject_manifest(ROOT,r,'core/ios-studio')
  self.assertEqual(len(s['components']),4);self.assertEqual(s['lockDigest'],digest(lock));self.assertEqual(s['sha256'],digest(manifest))
  e=self.evidence('structure')
  with self.assertRaises(Invalid):evidence_check(e,expected_subject=s)
 def test_build_reproducible_and_readback(self):
  one=build();two=build();self.assertEqual(one,two)
  for path,d in one.items():self.assertEqual(hashlib.sha256((ROOT/'dist'/path).read_bytes()).hexdigest(),d)
  with zipfile.ZipFile(ROOT/'dist/prototype.zip') as z:
   self.assertEqual(z.testzip(),None)
   self.assertTrue(all(x.date_time==(1980,1,1,0,0,0) for x in z.infolist()))
  self.assertEqual(len(read_json(ROOT/'dist/search-index.json')),len(load_catalog()))
 def test_publication_fails_closed(self):
  with self.assertRaises(Invalid):publication_gate(load_catalog())
 def test_synthetic_regression_oracle(self):
  f=read_json(ROOT/'evals/fixtures/regression-report.json');counts={s:sum(x['status']==s for x in f['input']['attempts']) for s in ['pass','fail','not-run']}
  for k,v in counts.items():self.assertEqual(v,f['expected'][k])
  self.assertGreater(counts['fail'],0);self.assertEqual(f['expected']['overall'],'fail')
 def test_native_yaml_type_and_syntax(self):
  with tempfile.TemporaryDirectory() as d:
   folder=Path(d)/'sample';folder.mkdir();p=folder/'SKILL.md'
   for value in ['true','null','123','# just a comment','""','"unterminated','[]','{}','false','~']:
    p.write_text('---\nname: sample\ndescription: '+value+'\n---\nBody\n')
    with self.subTest(value=value),self.assertRaises(Invalid):native_skill(p)
   for value in ['A useful description.','"true"',"'123'",'|\n  A multiline string.']:
    p.write_text('---\nname: sample\ndescription: '+value+'\n---\nBody\n');self.assertEqual(native_skill(p),'sample')
   p.write_text('---\nname: sample\ndescription: First\ndescription: Duplicate\n---\nBody\n')
   with self.assertRaises(Invalid):native_skill(p)
 def test_all_inputs_reject_symlinks(self):
  for relative in ['LICENSE','THIRD_PARTY_NOTICES.md','schemas/common.schema.json','schemas/agent.schema.json','site/assets/style.css','site/assets/search.js','skills/ios-test-plan/examples/toggle.md']:
   with self.subTest(path=relative),tempfile.TemporaryDirectory() as d:
    root=Path(d)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','dist','__pycache__'))
    outside=Path(d)/'outside.txt';outside.write_text('SYNTHETIC OUTSIDE BYTES')
    target=root/relative;target.unlink();target.symlink_to(outside)
    with self.assertRaises(Invalid):load_catalog(root)
 def test_nonlocal_schema_rejected(self):
  for keyword in ['$ref','$dynamicRef','$recursiveRef']:
   for schema_name in ['common','agent','evidence']:
    with self.subTest(keyword=keyword,schema=schema_name),tempfile.TemporaryDirectory() as d:
     root=Path(d)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','dist','__pycache__'))
     p=root/f'schemas/{schema_name}.schema.json';v=read_json(p);v[keyword]='https://example.invalid/schema';p.write_bytes(canonical(v))
     with self.assertRaises(Invalid):load_catalog(root)
     if schema_name!='common':
      record=self.evidence('structure') if schema_name=='evidence' else read_json(ROOT/'agents/ios-quality-reviewer/agent.json')
      with self.assertRaises(Invalid):validate_schema(record,schema_name,root=root)
 def test_stale_generated_cleanup_and_url_links(self):
  import build as builder
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','dist','__pycache__'))
   obsolete=root/'skills/ios-test-plan/examples/obsolete.txt';obsolete.write_text('synthetic obsolete')
   special=root/'skills/ios-test-plan/examples/ref#fragment.txt';special.write_text('synthetic special path')
   with patch.object(builder,'ROOT',root),patch.object(builder,'load_catalog',lambda:load_catalog(root)):
    builder.build();obsolete.unlink();checks=builder.build()
    self.assertFalse((root/'dist/source/skills/ios-test-plan/examples/obsolete.txt.txt').exists())
    page=(root/'dist/index.html').read_text();self.assertIn('ref%23fragment.txt.txt',page)
    self.assertTrue((root/'dist'/unquote('source/skills/ios-test-plan/examples/ref%23fragment.txt.txt')).is_file())
    self.assertEqual(set(checks)|{'checksums.json'}, {p.relative_to(root/'dist').as_posix() for p in (root/'dist').rglob('*') if p.is_file()})
    extra=root/'dist/user-owned.txt';extra.write_text('retain me')
    with self.assertRaises(Invalid):builder.build()
    self.assertEqual(extra.read_text(),'retain me')
 def test_modified_generated_output_preserved(self):
  import build as builder
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','dist','__pycache__'))
   with patch.object(builder,'ROOT',root),patch.object(builder,'load_catalog',lambda:load_catalog(root)):
    builder.build();p=root/'dist/index.html';p.write_text('user edit')
    with self.assertRaises(Invalid):builder.build()
    self.assertEqual(p.read_text(),'user edit')
 def test_receipt_symlink_rejected_before_read(self):
  import build as builder
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','dist','__pycache__'))
   with patch.object(builder,'ROOT',root),patch.object(builder,'load_catalog',lambda:load_catalog(root)):
    builder.build();receipt=root/'dist/checksums.json';receipt.unlink()
    outside=Path(d)/'outside.json';outside.write_text('{}');receipt.symlink_to(outside)
    with self.assertRaises(Invalid):builder.build()
 def test_original_work_license_and_official_text(self):
  expected='cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30'
  self.assertEqual(hashlib.sha256((ROOT/'LICENSE').read_bytes()).hexdigest(),expected)
  for info in load_catalog().values():self.assertEqual(info['record']['license'],'Apache-2.0')
  for p in (ROOT/'tests/fixtures').rglob('*.json'):
   item=read_json(p)
   if 'license' in item:self.assertEqual(item['license'],'Apache-2.0')
 def test_license_archive_and_catalog_readback(self):
  build()
  with zipfile.ZipFile(ROOT/'dist/prototype.zip') as z:
   self.assertEqual(z.read('LICENSE'),(ROOT/'LICENSE').read_bytes())
   self.assertEqual(z.read('THIRD_PARTY_NOTICES.md'),(ROOT/'THIRD_PARTY_NOTICES.md').read_bytes())
   self.assertIn(b'Apache-2.0',z.read('LICENSE-STATUS.txt'))
  page=(ROOT/'dist/index.html').read_text()
  self.assertEqual(page.count('license Apache-2.0'),len(load_catalog()))
  self.assertNotIn('License and identity unresolved',page)
  for b in read_json(ROOT/'dist/content-manifests.json').values():
   self.assertEqual({x['path'] for x in b['manifest']['files']} & {'LICENSE','THIRD_PARTY_NOTICES.md'},{'LICENSE','THIRD_PARTY_NOTICES.md'})
   self.assertTrue(all(x['license']=='Apache-2.0' for x in b['lock']['licenses']))
 def test_license_notice_changes_invalidate_subject(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d)/'repo';shutil.copytree(ROOT,root,ignore=shutil.ignore_patterns('.git','dist','__pycache__'))
   records=load_catalog(root);before=subject_manifest(root,records,'core/ios-studio')[0]['sha256']
   p=root/'THIRD_PARTY_NOTICES.md';p.write_text(p.read_text()+'\nSynthetic attribution amendment for digest test.\n')
   after=subject_manifest(root,records,'core/ios-studio')[0]['sha256'];self.assertNotEqual(before,after)
if __name__=='__main__':unittest.main()
