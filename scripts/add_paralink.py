#!/usr/bin/env python3
"""
Add paragraph permalink IDs to all chapter HTML files.
- Splits <p> content by newlines into logical paragraphs
- Wraps each in <span class="para" id="para-NNN">
- Skips entity-legend and entity-stats lines
- Adds <script src="../js/paralink.js"> before </body> if not present
- Handles 星庐概论 specially (already has per-paragraph <p> tags)
"""
import re
import os
import sys

CHAPTERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', 'chapters')
SPECIAL_BOOK = '20_星庐中国古天文学概论.html'


def process_file(filepath):
    """Process a single chapter HTML file."""
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Find the chapter-body content
    # Pattern: <div class="chapter-body..."> ... </div>
    body_start_pattern = r'(<div\s+class="chapter-body[^"]*">)'
    m = re.search(body_start_pattern, content)
    if not m:
        print(f"  SKIP {filename}: no .chapter-body found")
        return False

    body_start = m.end()

    # Find the closing </div> that matches this chapter-body
    # We need to track div nesting
    depth = 1
    pos = body_start
    while depth > 0 and pos < len(content):
        next_open = content.find('<div', pos)
        next_close = content.find('</div>', pos)
        if next_close == -1:
            break
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                body_end = next_close
                break
            pos = next_close + 6
    else:
        print(f"  SKIP {filename}: can't find closing </div> for chapter-body")
        return False

    body_content = content[body_start:body_end]
    before = content[:body_start]
    after = content[body_end:]

    # Special handling for 星庐概论 - it has proper <p> tags
    if filename == SPECIAL_BOOK:
        print(f"  Processing {filename} (special: multiple <p> tags)")
        para_num = 0

        def add_para_id(m):
            nonlocal para_num
            para_num += 1
            tag = m.group(0)
            # Don't modify if already has id
            if 'id=' in tag:
                return tag
            # Add id to <p> tag
            return tag.replace('<p>', f'<p id="para-{para_num:04d}">', 1)

        # Process <p> tags that don't already have ids
        body_content = re.sub(r'<p>', add_para_id, body_content)
        print(f"    Added {para_num} paragraph IDs")
    else:
        # Standard chapters: split the big <p> tag content
        # The structure is:
        #   <div class="entity-legend">...</div>
        #   <div class="entity-stats">...</div>
        #   <p>
        #   line1
        #   line2
        #   ...
        #   </p>
        #   </div>  (chapter-body)

        para_num = 0

        # Find all <p> tags in body_content and process each
        def process_p_tags(body):
            """Process <p>...</p> tags, splitting newlines into paragraphs."""
            nonlocal para_num
            result = []
            idx = 0

            while idx < len(body):
                p_start = body.find('<p>', idx)
                p_start2 = body.find('<p\n', idx)
                p_start3 = body.find('<p ', idx)
                
                # Find earliest <p> variant
                candidates = [(p_start, '<p>'), (p_start2, '<p\n'), (p_start3, '<p ')]
                valid = [(pos, tag) for pos, tag in candidates if pos != -1]
                
                if not valid:
                    result.append(body[idx:])
                    break
                
                p_start, p_tag = min(valid, key=lambda x: x[0])
                
                # Copy content before <p>
                result.append(body[idx:p_start])
                
                # Find matching </p>
                p_end = body.find('</p>', p_start)
                if p_end == -1:
                    result.append(body[p_start:])
                    break
                
                p_full = body[p_start:p_end + 4]
                p_inner = body[p_start + len(p_tag):p_end]
                
                # Check if this is entity-legend or entity-stats or too short
                # Skip if it's not a content paragraph
                if ('entity-legend' in p_full or 'entity-stats' in p_full or 
                    'img-ref' in p_full and len(p_inner.strip()) < 50):
                    result.append(p_full)
                    idx = p_end + 4
                    continue
                
                # Split inner content by newlines
                lines = p_inner.split('\n')
                wrapped_lines = []
                
                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        wrapped_lines.append(line)
                        continue
                    
                    # Skip short non-content lines
                    # Check if this line has actual Chinese text (not just HTML tags)
                    text_only = re.sub(r'<[^>]+>', '', stripped).strip()
                    if len(text_only) < 4:
                        wrapped_lines.append(line)
                        continue
                    
                    para_num += 1
                    para_id = f'para-{para_num:04d}'
                    wrapped_lines.append(
                        f'<span class="para" id="{para_id}">{stripped}</span>'
                    )
                
                p_new = '\n'.join(wrapped_lines)
                # Reconstruct <p> with wrapped content
                result.append(f'<p>\n{p_new}\n</p>\n')
                idx = p_end + 4
            
            return ''.join(result)
        
        body_content = process_p_tags(body_content)
        print(f"    Added {para_num} paragraph IDs")

    # Reassemble
    new_content = before + body_content + after

    # Add paralink.js script before </body> if not present
    if '../js/paralink.js' not in new_content and 'js/paralink.js' not in new_content:
        new_content = new_content.replace(
            '</body>',
            '<script src="../js/paralink.js"></script>\n</body>'
        )

    if new_content == original:
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


def main():
    print("Adding paragraph permalink IDs to chapter files...\n")
    
    modified = 0
    for filename in sorted(os.listdir(CHAPTERS_DIR)):
        if not filename.endswith('.html'):
            continue
        filepath = os.path.join(CHAPTERS_DIR, filename)
        if process_file(filepath):
            modified += 1
    
    print(f"\nDone! Modified {modified} files.")
    print("Now create docs/js/paralink.js and add CSS to style.css")


if __name__ == '__main__':
    main()
