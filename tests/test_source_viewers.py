"""Generated source readback/escaping tests; these do not establish browser rendering."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import build as builder
from library import ROOT, Invalid, load_catalog


class Viewer(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []; self.links = []; self.styles = []; self.policy = ''; self.source = ''; self.in_source = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs); self.tags.append(tag)
        if tag == 'a': self.links.append(attrs['href'])
        if tag == 'link': self.styles.append(attrs['href'])
        if tag == 'meta' and attrs.get('http-equiv') == 'Content-Security-Policy': self.policy = attrs['content']
        if tag == 'pre' and attrs.get('id') == 'source-text': self.in_source = True

    def handle_endtag(self, tag):
        if tag == 'pre': self.in_source = False

    def handle_data(self, value):
        if self.in_source: self.source += value


class SourceViewers(unittest.TestCase):
    def copy_root(self, parent):
        root = parent / 'candidate'
        shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git', 'dist', '__pycache__'))
        return root

    def build_at(self, root):
        with patch.object(builder, 'ROOT', root), patch.object(builder, 'load_catalog', lambda: load_catalog(root)):
            return builder.build()

    def assert_navigation(self, page_path, raw_path):
        viewer = Viewer(page_path.read_text())
        self.assertNotIn('script', viewer.tags)
        self.assertEqual(viewer.policy, "default-src 'none'; style-src 'self'; base-uri 'none'; form-action 'none'")
        self.assertEqual((page_path.parent / unquote(viewer.links[1])).resolve(), raw_path.resolve())
        catalog = (page_path.parent / unquote(viewer.links[0])).resolve()
        self.assertEqual(catalog.name, 'index.html')
        self.assertEqual((page_path.parent / unquote(viewer.styles[0])).resolve(), catalog.parent / 'style.css')
        self.assertEqual(viewer.links[2], 'https://github.com/sha-shank-03/tessuno')
        for link in viewer.links[:2] + viewer.styles:
            self.assertTrue((page_path.parent / unquote(link)).is_file(), link)
        return viewer

    def test_manifest_source_and_metadata_viewers_preserve_bytes(self):
        checks = builder.build(); dist = ROOT / 'dist'
        manifests = json.loads((dist / 'content-manifests.json').read_text())
        entries = {entry['path']: entry for bundle in manifests.values() for entry in bundle['manifest']['files']}
        for path, entry in entries.items():
            with self.subTest(path=path):
                raw = dist / ('source/' + path + '.txt'); page = dist / ('source/' + path + '.html')
                original = (ROOT / path).read_bytes()
                self.assertEqual(raw.read_bytes(), original)
                self.assertEqual(hashlib.sha256(original).hexdigest(), entry['sha256'])
                viewer = self.assert_navigation(page, raw)
                self.assertEqual(viewer.source, original.decode('utf-8'))
                self.assertIn(hashlib.sha256(original).hexdigest(), page.read_text())
                self.assertIn(page.relative_to(dist).as_posix(), checks)
        index = (dist / 'index.html').read_text()
        for name in ('content-manifests', 'search-index'):
            raw = dist / (name + '.json'); page = dist / (name + '.html')
            self.assertEqual(self.assert_navigation(page, raw).source, raw.read_text())
            self.assertIn('href="' + name + '.html"', index)
        self.assertEqual(checks, builder.build())

    def test_hostile_markup_and_special_filename_are_visible_data(self):
        text = '</code></pre><script>window.sourceExecuted=true</script><img src=x onerror=alert(1)>\nA & B "quote" café 東京\n'
        with tempfile.TemporaryDirectory() as folder:
            root = self.copy_root(Path(folder)); path = "skills/ios-test-plan/examples/ref#quote'&.md"
            (root / path).write_text(text)
            self.build_at(root)
            page = root / ('dist/source/' + path + '.html'); raw = root / ('dist/source/' + path + '.txt')
            viewer = self.assert_navigation(page, raw)
            self.assertEqual(viewer.source, text)
            self.assertNotIn('img', viewer.tags); self.assertNotIn('script', viewer.tags)
            self.assertEqual(raw.read_text(), text)
            index = (root / 'dist/index.html').read_text()
            self.assertIn('ref%23quote%27%26.md.html', index)
            self.assertIn('ref%23quote%27%26.md.txt', index)
            self.assertIn('&lt;script&gt;', page.read_text())

    def test_binary_source_keeps_bytes_and_labels_unavailable_text(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.copy_root(Path(folder)); path = 'skills/ios-test-plan/examples/synthetic.txt'
            data = b'\xff\xfe\x00\x01'; (root / path).write_bytes(data)
            self.build_at(root)
            page = root / ('dist/source/' + path + '.html'); raw = root / ('dist/source/' + path + '.txt')
            viewer = self.assert_navigation(page, raw)
            self.assertNotIn('pre', viewer.tags)
            self.assertIn('UTF-8 text preview unavailable', page.read_text())
            self.assertIn(hashlib.sha256(data).hexdigest(), page.read_text())
            self.assertEqual(raw.read_bytes(), data)

    def test_stale_viewer_cleanup_and_edited_viewer_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.copy_root(Path(folder)); source = root / 'skills/ios-test-plan/examples/obsolete.md'
            source.write_text('original synthetic source')
            self.build_at(root); source.unlink(); checks = self.build_at(root)
            for suffix in ('.html', '.txt'):
                name = 'source/skills/ios-test-plan/examples/obsolete.md' + suffix
                self.assertNotIn(name, checks); self.assertFalse((root / 'dist' / name).exists())
            viewer = root / 'dist/source/skills/ios-test-plan/SKILL.md.html'
            viewer.write_text('retain user edit')
            with self.assertRaisesRegex(Invalid, 'modified generated output'):
                self.build_at(root)
            self.assertEqual(viewer.read_text(), 'retain user edit')


if __name__ == '__main__':
    unittest.main()
