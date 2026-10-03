"""Metadata/readback tests; Node harness checks behavior, not browser accessibility."""
import json
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build import build
from library import ROOT, load_catalog


class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.cards = []; self.options = {}; self.select = None; self.links = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article': self.cards.append(attrs)
        if tag == 'select': self.select = attrs['id']; self.options[self.select] = []
        if tag == 'option': self.options[self.select].append(attrs['value'])
        if tag == 'a': self.links.append(attrs['href'])
    def handle_endtag(self, tag):
        if tag == 'select': self.select = None


class CatalogFilters(unittest.TestCase):
    def test_metadata_options_cards_and_source_links(self):
        build(); page = Page(); page.feed((ROOT / 'dist/index.html').read_text())
        records = [info['record'] for _, info in sorted(load_catalog().items())]
        self.assertEqual(page.options['kind'], [''] + sorted({r['kind'] for r in records}))
        self.assertEqual(page.options['stack'], [''] + sorted({s for r in records for s in r['stacks']}))
        self.assertEqual(len(page.cards), len(records))
        for card, record in zip(page.cards, records):
            self.assertEqual(card['data-kind'], record['kind'])
            self.assertEqual(json.loads(card['data-stacks']), record['stacks'])
        sources = [link for link in page.links if link.startswith('source/')]
        self.assertTrue(sources)
        self.assertTrue(all((ROOT / 'dist' / link).is_file() for link in sources))
        html = (ROOT / 'dist/index.html').read_text()
        self.assertIn('no authenticated runtime evidence', html)
        self.assertIn('All objects and source links are available below without JavaScript.', html)
        self.assertIn('id="count" role="status"', html)

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable: JS behavior not checked')
    def test_combined_search_exact_filters_empty_and_reset(self):
        harness = r'''
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
function control() { return {value:'', disabled:true, handlers:{}, addEventListener(e,f){this.handlers[e]=f}, focus(){this.focused=true}}; }
const controls = Object.fromEntries(['search','kind','stack','reset','count','empty'].map(id=>[id,control()]));
const cards = [
 {dataset:{kind:'Skill',stacks:'["ios","swift"]',search:'Skill ios swift test plan'}},
 {dataset:{kind:'Agent',stacks:'["ios"]',search:'Agent ios review'}},
 {dataset:{kind:'Skill',stacks:'["web"]',search:'Skill web review'}}];
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),{document:{querySelector:s=>controls[s.slice(1)],querySelectorAll:()=>cards}});
const visible=()=>cards.filter(c=>!c.hidden).length;
assert.equal(visible(),3); assert.equal(controls.count.textContent,'3 of 3 objects');
for(const id of ['search','kind','stack','reset']) assert.equal(controls[id].disabled,false);
controls.kind.value='Skill'; controls.kind.handlers.change(); assert.equal(visible(),2);
controls.stack.value='ios'; controls.stack.handlers.change(); assert.equal(visible(),1);
controls.stack.value='io'; controls.stack.handlers.change(); assert.equal(visible(),0); // exact stack membership
controls.stack.value='ios'; controls.search.value='  TEST  plan '; controls.search.handlers.input(); assert.equal(visible(),1);
controls.search.value='no-such-object'; controls.search.handlers.input(); assert.equal(visible(),0); assert.equal(controls.empty.hidden,false);
controls.reset.handlers.click(); assert.equal(visible(),3); assert.equal(controls.empty.hidden,true); assert.equal(controls.search.focused,true);
controls.search.value='<script>'; controls.search.handlers.input(); assert.equal(visible(),0);
console.log('PASS: combined filtering, exact stacks, empty state, reset/focus; mocked DOM only');
'''
        result = subprocess.run([shutil.which('node'), '-e', harness, str(ROOT / 'site/assets/search.js')], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
