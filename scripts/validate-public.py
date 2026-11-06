#!/usr/bin/env python3
"""Validate the explicit public source inventory and local HTML links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    '.gitignore', '.claude-plugin/plugin.json', '.mcp.json', 'LICENSE',
    'README.md', 'CHANGELOG.md', 'skills/inspect-project/SKILL.md',
    'docs/index.html', 'docs/ru.html', 'docs/guide.css', 'docs/guide.js',
    'docs/.nojekyll', 'docs/sitemap.xml', 'docs/oauth-status.json',
    'docs/listing.en.json', 'docs/listing.ru.json', 'docs/review-cases.json',
    'docs/connector-listing.en.json', 'docs/connector-listing.ru.json',
    'docs/reviewer-guide.md', 'docs/assets/tvijo-icon-256.png',
    'review-fixture/README.md', 'review-fixture/app.py', 'review-fixture/notes/release.txt',
    'scripts/build-package.py', 'scripts/check-oauth.py', 'scripts/validate-public.py',
}
SECRET = re.compile(rb'(?m)^-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}')
PRIVATE = (b'/root/', b'/mnt/HC_', b'127.0.0.1:8787')

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.path = path; self.ids = set(); self.refs = []; self.h1 = 0; self.lang = None
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'html': self.lang = d.get('lang')
        if tag == 'h1': self.h1 += 1
        if 'id' in d:
            assert d['id'] not in self.ids, f'duplicate id {self.path}:{d["id"]}'
            self.ids.add(d['id'])
        for key in ('href', 'src'):
            if key in d: self.refs.append(d[key])

def main():
    raw = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT)
    paths = set(filter(None, raw.decode().split('\0')))
    assert paths == ALLOWED, f'inventory difference: {sorted(paths ^ ALLOWED)}'
    for name in sorted(paths):
        p = ROOT / name
        assert not p.is_symlink() and p.is_file(), f'nonportable file: {name}'
        raw = p.read_bytes()
        assert len(raw) < 250000, f'oversized: {name}'
        assert not SECRET.search(raw), f'credential-like content: {name}'
        if name != 'scripts/validate-public.py':
            assert not any(s in raw for s in PRIVATE), f'private host reference: {name}'
    manifest = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
    assert manifest['license'] == 'MIT'
    assert manifest['name'] == 'tvijo-remdesk'
    assert (ROOT / 'LICENSE').read_text().startswith('MIT License\n')
    mcp = json.loads((ROOT / '.mcp.json').read_text())
    assert mcp == {'mcpServers': {'remdesk': {'type': 'http', 'url': 'https://mcp.tvijo.com/mcp'}}}
    pages = {}
    for name, language in [('index.html','en'), ('ru.html','ru')]:
        p = ROOT / 'docs' / name; page = Page(p); page.feed(p.read_text())
        assert page.h1 == 1 and page.lang == language
        assert {f'step-{i}' for i in range(1,10)} <= page.ids
        pages[p.resolve()] = page
    count = 0
    for path, page in pages.items():
        for ref in page.refs:
            u = urlsplit(ref)
            if u.scheme or u.netloc: continue
            target = (path.parent / unquote(u.path)).resolve() if u.path else path
            assert target.is_relative_to(ROOT) and target.is_file(), f'broken local link: {path.name} {ref}'
            if u.fragment and target in pages:
                assert u.fragment in pages[target].ids, f'broken anchor: {ref}'
            count += 1
    status = json.loads((ROOT / 'docs/oauth-status.json').read_text())
    assert status['fully_integrated'] is False
    assert status['claude_end_to_end_oauth'] == 'NOT_RUN'
    print(json.dumps({'public_files':len(paths), 'local_links_checked':count,
                      'secret_and_private_path_scan':'PASS', 'html_structure':'PASS',
                      'runtime_claims':'CLAUDE_OAUTH_NOT_RUN'}, indent=2))
if __name__ == '__main__': main()
