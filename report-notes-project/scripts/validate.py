"""Zero-dependency repository validation: python scripts/validate.py"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ISSUES = []


def problem(message):
    ISSUES.append(message)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.h1_count = 0
        self.title_count = 0
        self.language = None
        self.in_h1 = False
        self.h1_text = ''
        self.in_title = False
        self.title_text = ''

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.language = a.get('lang')
        if 'id' in a:
            if a['id'] in self.ids:
                problem(f'Duplicate id: {a["id"]}')
            self.ids.add(a['id'])
        if tag in ('a', 'link', 'script', 'img'):
            key = 'href' if tag in ('a', 'link') else 'src'
            if a.get(key):
                self.links.append(a[key])
        if tag == 'h1':
            self.h1_count += 1
            self.in_h1 = True
        if tag == 'title':
            self.title_count += 1
            self.in_title = True

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False
        if tag == 'title':
            self.in_title = False

    def handle_data(self, data):
        if self.in_h1:
            self.h1_text += data
        if self.in_title:
            self.title_text += data


def parse(path):
    p = PageParser()
    try:
        p.feed(path.read_text(encoding='utf-8'))
    except Exception as ex:
        problem(f'{path.relative_to(ROOT)}: invalid HTML input ({ex})')
    return p


all_pages = list(ROOT.rglob('*.html'))
parsed = {p: parse(p) for p in all_pages}
for file, p in parsed.items():
    rel = file.relative_to(ROOT)
    if p.h1_count != 1:
        problem(f'{rel}: expected one h1, found {p.h1_count}')
    if p.title_count != 1:
        problem(f'{rel}: expected one title, found {p.title_count}')
    if p.language != 'zh-Hant':
        problem(f'{rel}: html lang should be zh-Hant')
    if file.name != '_template.html' and re.search(r'【[^】]+】', file.read_text(encoding='utf-8')):
        problem(f'{rel}: unfilled placeholder')
    for link in p.links:
        if link.startswith(('http:', 'https:', 'mailto:', 'tel:', 'data:')):
            continue
        if link.startswith('/') or link.startswith('javascript:'):
            problem(f'{rel}: prohibited absolute/unsafe link: {link}')
            continue
        url = urlsplit(link)
        target = (file.parent / unquote(url.path)).resolve() if url.path else file
        if not target.is_relative_to(ROOT):
            problem(f'{rel}: link escapes repository: {link}')
        elif not target.is_file():
            problem(f'{rel}: broken link: {link}')
        elif url.fragment and target.suffix == '.html' and target in parsed and unquote(url.fragment) not in parsed[target].ids:
            problem(f'{rel}: missing anchor: {link}')

raw = (ROOT / 'data/articles.js').read_text(encoding='utf-8')
match = re.search(r'window\.REPORT_ARTICLES\s*=\s*(\[.*\])\s*;', raw, re.S)
if not match:
    problem('data/articles.js: missing REPORT_ARTICLES array')
    articles = []
else:
    try:
        articles = json.loads(match.group(1))
    except json.JSONDecodeError as ex:
        problem(f'data/articles.js: not JSON-compatible ({ex})')
        articles = []

seen_ids, seen_paths, seen_numbers = set(), set(), set()
index_source = (ROOT / 'index.html').read_text(encoding='utf-8')
filters = set(re.findall(r'data-filter="([^"]+)"', index_source))
for a in articles:
    for required in ('id', 'title', 'subtitle', 'category', 'level', 'minutes', 'number', 'path', 'tags'):
        if required not in a:
            problem(f'Metadata missing {required}: {a}')
    slug, path = a.get('id',''), a.get('path','')
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        problem(f'Invalid slug: {slug}')
    if path != f'pages/{slug}.html':
        problem(f'Path/id mismatch: {path} / {slug}')
    if slug in seen_ids or path in seen_paths or a.get('number') in seen_numbers:
        problem(f'Duplicate metadata id/path/number: {slug}')
    seen_ids.add(slug)
    seen_paths.add(path)
    seen_numbers.add(a.get('number'))
    if not isinstance(a.get('minutes'), int) or a.get('minutes', 0) <= 0:
        problem(f'Invalid reading minutes: {slug}')
    if a.get('category') not in filters:
        problem(f'Missing category filter for {slug}')
    target = ROOT / path
    if not target.is_file():
        problem(f'Article file missing: {path}')
    elif a.get('title') not in parsed[target].h1_text:
        problem(f'{path}: h1 does not match metadata title')

for page in ROOT.glob('pages/*.html'):
    if page.name != '_template.html' and f'pages/{page.name}' not in seen_paths:
        problem(f'{page.relative_to(ROOT)}: page missing metadata')

if ISSUES:
    print(f'FAILED with {len(ISSUES)} issue(s):')
    for issue in ISSUES:
        print(' -', issue)
    sys.exit(1)
print(f'PASS: {len(all_pages) - 1} published HTML files, {len(articles)} article records, all internal links and anchors verified.')
