"""Offline navigation/readback checks; mocked DOM does not qualify a browser."""
from collections import defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build as builder
from library import ROOT, load_catalog


class Navigation(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.cards = {}; self.card = None; self.details = 0
        self.links = []; self.tags = []; self.title = ''; self.in_title = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs); self.tags.append(tag)
        if tag == 'title': self.in_title = True
        if tag == 'article':
            self.card = attrs['id']; self.cards[self.card] = {'attrs': attrs, 'visibleLinks': []}
        if tag == 'details': self.details += 1
        if tag == 'a':
            self.links.append(attrs['href'])
            if self.card and not self.details:
                self.cards[self.card]['visibleLinks'].append(attrs['href'])

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'article': self.card = None
        if tag == 'details': self.details -= 1

    def handle_data(self, value):
        if self.in_title: self.title += value


class CatalogNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        builder.build()

    def test_visible_object_links_exact_contracts_and_native_entries(self):
        page = Navigation((ROOT / 'dist/index.html').read_text())
        records = load_catalog()
        self.assertEqual(set(page.cards), {'object-' + id for id in records})
        for id, info in records.items():
            with self.subTest(id=id):
                card = page.cards['object-' + id]
                self.assertEqual(card['attrs']['tabindex'], '-1')
                links = card['visibleLinks']
                self.assertIn('object-' + id, [unquote(urlsplit(link).fragment) for link in links])
                source = info['path'].relative_to(ROOT).as_posix()
                targets = {unquote(urlsplit(link).path) for link in links}
                self.assertIn('source/' + source + '.html', targets)
                if info['record']['kind'] == 'Skill':
                    entry = info['path'].parent / info['record']['entry']
                    self.assertIn('source/' + entry.relative_to(ROOT).as_posix() + '.html', targets)
                for target in targets - {''}:
                    self.assertTrue((ROOT / 'dist' / target).is_file())

    def test_source_backlinks_match_exact_closure_including_shared_files(self):
        dist = ROOT / 'dist'
        manifests = json.loads((dist / 'content-manifests.json').read_text())
        expected = defaultdict(set)
        for id, bundle in manifests.items():
            for entry in bundle['manifest']['files']: expected[entry['path']].add('object-' + id)
        self.assertEqual(len(expected['LICENSE']), len(manifests))
        for source, ids in expected.items():
            with self.subTest(source=source):
                path = dist / ('source/' + source + '.html')
                page = Navigation(path.read_text())
                backlinks = [urlsplit(link) for link in page.links if urlsplit(link).fragment]
                self.assertEqual(len(backlinks), len(ids))
                self.assertEqual({unquote(link.fragment) for link in backlinks}, ids)
                for link in backlinks:
                    self.assertEqual((path.parent / unquote(link.path)).resolve(), dist / 'index.html')
                self.assertEqual(page.title, source + ' · Tessuno source')
                self.assertNotIn('script', page.tags)
        for name in ('content-manifests', 'search-index'):
            page = Navigation((dist / (name + '.html')).read_text())
            self.assertFalse(any(urlsplit(link).fragment for link in page.links))

    def test_object_fragments_do_not_collide_for_valid_separator_ids(self):
        ids = ['core--ios/review', 'core/ios--review']
        self.assertEqual(len({builder.object_anchor(id) for id in ids}), 2)
        for id in ids:
            self.assertEqual(unquote(builder.object_link(id)[1:]), builder.object_anchor(id))

    def test_untrusted_titles_and_special_paths_remain_escaped_data(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'candidate'
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__'))
            sidecar = root / 'skills/ios-test-plan/library.json'
            item = json.loads(sidecar.read_text())
            title = '</a><script>alert(1)</script><img src=x onerror=alert(1)> & café'
            item['title'] = title; sidecar.write_text(json.dumps(item))
            source = "skills/ios-test-plan/examples/ref#quote'&.md"
            data = b'Original synthetic bytes\r\n'
            (root / source).write_bytes(data)
            with patch.object(builder, 'ROOT', root), patch.object(builder, 'load_catalog', lambda: load_catalog(root)):
                first = builder.build(); self.assertEqual(first, builder.build())
            path = root / ('dist/source/' + source + '.html')
            page = Navigation(path.read_text())
            self.assertEqual(page.title, source + ' · Tessuno source')
            self.assertNotIn('script', page.tags); self.assertNotIn('img', page.tags)
            self.assertIn('&lt;script&gt;', path.read_text())
            self.assertTrue(any(unquote(urlsplit(link).fragment) == 'object-' + item['id'] for link in page.links))
            self.assertEqual((root / ('dist/source/' + source + '.txt')).read_bytes(), data)

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable: fragment behavior not checked')
    def test_fragments_reveal_known_filtered_objects_and_ignore_invalid_targets(self):
        harness = r'''
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
function start(hash) {
  const controls = Object.fromEntries(['search','kind','stack','reset','count','empty'].map(id =>
    [id,{value:'',handlers:{},addEventListener(e,f){this.handlers[e]=f},focus(){this.focused=true}}]));
  const cards = [
    {id:'object-core/skill',dataset:{kind:'Skill',stacks:'["ios"]',search:'Skill ios'}},
    {id:'object-core/reviewer',dataset:{kind:'Agent',stacks:'["web"]',search:'Agent web'}}];
  const actions = [];
  for(const card of cards) {
    card.focus=()=>actions.push(['focus',card.id]);
    card.scrollIntoView=options=>actions.push(['scroll',card.id,options.block]);
  }
  const window = {location:{hash},handlers:{},addEventListener(e,f){this.handlers[e]=f}};
  const pending = new Map(); let timerId=0;
  const setTimeout=fn=>{pending.set(++timerId,fn);return timerId;};
  const clearTimeout=id=>pending.delete(id);
  const flush=()=>{const callbacks=[...pending.values()];pending.clear();for(const fn of callbacks)fn();};
  vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{window,setTimeout,clearTimeout,document:{
    querySelector:s=>controls[s.slice(1)],querySelectorAll:()=>cards}});
  return {controls,cards,window,actions,pending,flush};
}
const {controls,cards,window,actions,pending,flush} = start('');
controls.search.value='ios'; controls.kind.value='Skill'; controls.stack.value='ios';
controls.search.handlers.input(); assert.equal(cards[1].hidden,true);
window.location.hash='#object-core%2Freviewer'; window.handlers.hashchange();
for(const id of ['search','kind','stack']) assert.equal(controls[id].value,'');
assert.equal(cards[1].hidden,false); assert.equal(controls.count.textContent,'2 of 2 objects');
assert.deepEqual(actions,[['focus','object-core/reviewer'],['scroll','object-core/reviewer','start']]);
controls.search.value='no-match'; controls.search.handlers.input();
for(const hash of ['', '#object-core%2Funknown', '#%E0%A4%A', '#__proto__', '#object-core/reviewer%22%5D']) {
  window.location.hash=hash; window.handlers.hashchange();
  assert.equal(controls.search.value,'no-match'); assert.equal(cards[1].hidden,true);
  assert.equal(actions.length,2);
}
const initial = start('#object-core%2Fskill');
assert.equal(initial.actions[0][1],'object-core/skill');
assert.equal(initial.cards[0].hidden,false);
window.location.hash='#object-core/reviewer'; window.handlers.hashchange();
assert.equal(cards[1].hidden,false); assert.equal(controls.empty.hidden,true);
controls.search.value='ios'; controls.search.handlers.input(); assert.equal(cards[1].hidden,true);
window.handlers.pageshow({persisted:false}); assert.equal(cards[1].hidden,true); flush();
assert.equal(controls.search.value,''); assert.equal(cards[1].hidden,false);
controls.search.value='ios'; controls.search.handlers.input(); assert.equal(cards[1].hidden,true);
const beforeRestore=actions.length;
window.handlers.pageshow({persisted:true});
assert.equal(actions.length,beforeRestore); // browser restoration has not finished
controls.kind.value='Skill'; // browser restores form values after pageshow
window.handlers.popstate(); assert.equal(pending.size,1); flush();
assert.equal(controls.search.value,''); assert.equal(cards[1].hidden,false);
assert.equal(controls.kind.value,'');
assert.equal(actions.length,beforeRestore+2);
assert.equal(actions[beforeRestore][1],'object-core/reviewer');
controls.search.value='no-match'; controls.search.handlers.input();
window.location.hash='#unknown'; window.handlers.pageshow({persisted:true});
flush();
assert.equal(controls.search.value,'no-match'); assert.equal(cards[1].hidden,true);
// A later navigation cancels an obsolete target; deferred work reads current state.
window.location.hash='#object-core/skill'; window.handlers.popstate();
window.location.hash='#unknown'; window.handlers.pageshow({persisted:false});
const beforeCancel=actions.length; assert.equal(pending.size,1); flush();
assert.equal(actions.length,beforeCancel); assert.equal(controls.search.value,'no-match');
// With no known fragment, restored filters must agree with cards/count after history.
window.location.hash=''; window.handlers.pageshow({persisted:false});
controls.search.value=''; controls.kind.value='Skill'; controls.stack.value='ios'; flush();
assert.equal(cards[0].hidden,false); assert.equal(cards[1].hidden,true);
assert.equal(controls.count.textContent,'1 of 2 objects');
console.log('PASS: fragments, invalid targets, deferred history/form restoration and cancellation; mocked DOM only');
'''
        result = subprocess.run([shutil.which('node'), '-e', harness, str(ROOT / 'site/assets/search.js')],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__': unittest.main()
