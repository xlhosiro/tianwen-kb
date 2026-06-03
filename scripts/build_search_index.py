#!/usr/bin/env python3
"""
Build search index for tianwen-kb static site.
Extracts text from all 20 chapter HTML files, generates pinyin,
builds MiniSearch-compatible index + suggestions list.
Output: docs/data/search-index.json (~2-5 MB)
"""
import re
import json
import os
import sys
from html.parser import HTMLParser
from pypinyin import lazy_pinyin, Style

DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
CHAPTERS_DIR = os.path.join(DOCS_DIR, 'chapters')
ENTITY_DATA = os.path.join(DOCS_DIR, 'kg', 'entity_data.js')
KG_CROSS = os.path.join(DOCS_DIR, 'kg', 'kg_cross_data.js')
OUTPUT = os.path.join(DOCS_DIR, 'data', 'search-index.json')

class TextExtractor(HTMLParser):
    """Extract text from HTML, tracking paragraph boundaries via <span class="para">."""
    def __init__(self):
        super().__init__()
        self.paragraphs = []
        self.current_text = []
        self.current_heading = ""
        self.in_body = False
        self.in_header = False
        self.skip_script = False
        self.current_para_id = None

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get('class', '')
        pid = attrs_dict.get('id', '')
        if tag == 'script':
            self.skip_script = True
        if tag == 'div' and 'chapter-body' in cls:
            self.in_body = True
        if tag == 'div' and 'chapter-header' in cls:
            self.in_header = True
        if tag in ('h2', 'h3', 'h4'):
            self._flush()
            self.current_heading = ""
        # Flush on <span class="para"> — these are the real paragraph boundaries
        if tag == 'span' and 'para' in cls:
            self._flush()
            self.current_para_id = pid

    def handle_endtag(self, tag):
        if tag == 'script':
            self.skip_script = False
        if tag in ('p', 'h2', 'h3', 'h4', 'li', 'blockquote'):
            self._flush()
        if tag == 'div':
            pass  # don't flush on div close

    def handle_data(self, data):
        if self.skip_script or not self.in_body:
            return
        text = data.strip()
        if text:
            self.current_text.append(text)

    def _flush(self):
        text = ' '.join(self.current_text).strip()
        text = re.sub(r'\s+', ' ', text)
        if text and len(text) > 2:
            self.paragraphs.append({
                'text': text,
                'heading': self.current_heading,
                'para_id': self.current_para_id
            })
        self.current_text = []
        self.current_para_id = None


def extract_chapter_text(html_path):
    """Extract paragraphs from a chapter HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    extractor = TextExtractor()
    extractor.feed(html)
    return extractor.paragraphs


def get_pinyin(text):
    """Get pinyin (no tones, space-separated) for a Chinese text."""
    pinyin_parts = lazy_pinyin(text, style=Style.NORMAL, errors='ignore')
    return ' '.join(pinyin_parts)


def load_entity_names():
    """Load entity names from entity_data.js for suggestions."""
    entity_names = set()
    if os.path.exists(ENTITY_DATA):
        with open(ENTITY_DATA, 'r', encoding='utf-8') as f:
            content = f.read()
        # Extract entity names from JSON
        # Format: window.ENTITIES=[{"name":"太白",...},...]
        try:
            # Find the JSON array
            start = content.index('[{')
            end = content.rindex('}]') + 2
            json_str = content[start:end]
            entities = json.loads(json_str)
            for e in entities:
                name = e.get('name', '').strip()
                # Filter out garbage (references with [M, [J etc)
                if name and len(name) >= 2 and len(name) <= 20:
                    # Skip citation-like names
                    if not re.search(r'[\[\(\d]', name):
                        entity_names.add(name)
        except Exception as e:
            print(f"Warning: could not parse entity_data.js: {e}")

    # Also add event type names from kg_cross_data.js
    if os.path.exists(KG_CROSS):
        with open(KG_CROSS, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            start = content.index('[')
            end = content.rindex(']') + 1
            json_str = content[start:end]
            events = json.loads(json_str)
            for ev in events:
                desc = ev.get('description', '')
                # Extract entity names from descriptions
                # e.g. "荧惑守心" -> useful suggestion
                if desc and len(desc) <= 20:
                    entity_names.add(desc)
        except Exception as e:
            print(f"Warning: could not parse kg_cross_data.js: {e}")

    return sorted(entity_names)


def build_index():
    """Main function: build search index."""
    print("Building search index...")

    # Load books metadata
    chapters_json = os.path.join(DOCS_DIR, 'data', 'chapters.json')
    with open(chapters_json, 'r', encoding='utf-8') as f:
        books = json.load(f)

    # Map book IDs to metadata
    book_map = {b['id']: b for b in books}

    documents = []
    suggestions = set()
    total_paragraphs = 0

    for book in books:
        bid = book['id']
        # Find chapter file
        url = book.get('url', '')
        filename = os.path.basename(url)
        html_path = os.path.join(CHAPTERS_DIR, filename)

        if not os.path.exists(html_path):
            print(f"  SKIP: {filename} not found")
            continue

        print(f"  Processing: {book['book']} · {book['chapter']}")

        # Extract book title + chapter as title document
        title_text = f"{book['book']} {book['chapter']} {book['dynasty']} {book['author']} {book.get('description', '')}"
        pinyin = get_pinyin(title_text)
        pinyin_nospace = pinyin.replace(' ', '')

        # Title document
        doc = {
            'id': f"{bid}_title",
            'book': book['book'],
            'chapter': book['chapter'],
            'dynasty': book['dynasty'],
            'author': book.get('author', ''),
            'url': url,
            'type': 'title',
            'text': title_text,
            'pinyin': pinyin,
            'pinyin_nospace': pinyin_nospace,
            'heading': ''
        }
        documents.append(doc)

        # Add book name to suggestions
        suggestions.add(book['book'])
        suggestions.add(book['chapter'])
        suggestions.add(book.get('author', ''))

        # Extract body paragraphs
        paragraphs = extract_chapter_text(html_path)
        for i, p in enumerate(paragraphs):
            text = p['text']
            if len(text) < 4:
                continue

            anchor = p.get('para_id') or f"p{i:04d}"
            if anchor and anchor.startswith('para-'):
                anchor = anchor
            else:
                anchor = f"para-{anchor}" if anchor and not anchor.startswith('para-') else f"para-{i:04d}"
            # Extract numeric part for stable doc id (e.g. "para-0035" → "0035")
            para_num = anchor.replace('para-', '') if anchor else f"{i:04d}"
            pid = f"{bid}_p{para_num}"
            pinyin = get_pinyin(text)
            pinyin_nospace = pinyin.replace(' ', '')

            doc = {
                'id': pid,
                'book': book['book'],
                'chapter': book['chapter'],
                'dynasty': book['dynasty'],
                'author': book.get('author', ''),
                'url': f"{url}",
                'type': 'body',
                'text': text,
                'pinyin': pinyin,
                'pinyin_nospace': pinyin_nospace,
                'heading': p.get('heading', '')
            }
            documents.append(doc)
            total_paragraphs += 1

    # Load entity names for suggestions
    print("\nLoading entity suggestions...")
    entity_suggestions = load_entity_names()
    suggestions.update(entity_suggestions)

    # Build final suggestions list with pinyin
    suggestions_list = []
    for name in sorted(suggestions):
        if len(name) >= 2 and len(name) <= 30:
            pinyin = get_pinyin(name)
            suggestions_list.append({
                'text': name,
                'pinyin': pinyin
            })

    # Build output
    output = {
        'version': 1,
        'total_documents': len(documents),
        'total_paragraphs': total_paragraphs,
        'books': len(books),
        'documents': documents,
        'suggestions': suggestions_list
    }

    # Write output
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, separators=(',', ':'))

    file_size = os.path.getsize(OUTPUT)
    print(f"\nDone! Output: {OUTPUT}")
    print(f"  Documents: {len(documents)}")
    print(f"  Paragraphs: {total_paragraphs}")
    print(f"  Suggestions: {len(suggestions_list)}")
    print(f"  File size: {file_size / 1024:.0f} KB")


if __name__ == '__main__':
    build_index()
