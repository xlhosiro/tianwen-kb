#!/usr/bin/env python3
"""Rebuild 占星回廊 HTML from markdown — fix image popup + escape issues."""
import re, os, json
from html import escape

md_path = r'D:\24history\twz\占星回廊.md'
img_dir = r'D:\24history\twz\tianwen-kb\docs\chapters\images'
out_path = r'D:\24history\twz\tianwen-kb\docs\chapters\24_星庐_占星回廊.html'

with open(md_path, 'r', encoding='utf-8') as f:
    md_text = f.read()

TITLE = '星庐·天文占星学的历史传播与哲学性研究'
AUTHOR='***'
DYNASTY = '当代'
DESC = '以东西方星官与星座的整合研究为线索，从楚帛书五行令到太乙观星法，系统阐述天文占星学的历史传播路径及其背后的哲学思想。'

# Parse markdown into blocks
blocks = []
for block in re.split(r'\n\n+', md_text):
    block = block.strip()
    if not block:
        continue
    blocks.append(block)

toc_items = []
body_parts = []
para_id = 1

for block in blocks:
    lines = block.split('\n')
    first = lines[0].strip()
    
    # Heading detection
    if first.startswith('# '):
        hid = f'sec-{len(toc_items)}'
        toc_items.append((1, first[2:], hid))
        body_parts.append(f'<h2 id="{hid}">{escape(first[2:])}</h2>')
        continue
    if first.startswith('## '):
        hid = f'sec-{len(toc_items)}'
        toc_items.append((2, first[3:], hid))
        body_parts.append(f'<h3 id="{hid}">{escape(first[3:])}</h3>')
        continue
    if first.startswith('### '):
        hid = f'sec-{len(toc_items)}'
        toc_items.append((3, first[4:], hid))
        body_parts.append(f'<h4 id="{hid}">{escape(first[4:])}</h4>')
        continue
    
    # Poetry block (consecutive short lines without punctuation)
    if all(len(l.strip()) < 40 and not any(c in l for c in '，。') for l in lines[:4]):
        body_parts.append(f'<div class="poem-block">{"<br>".join(escape(l.strip()) for l in lines)}</div>')
        continue
    
    # Tips block
    if first.startswith('> '):
        tip_text = first[2:].strip()
        body_parts.append(f'<div class="tips-box"><strong>💡 提示</strong><p>{escape(tip_text)}</p></div>')
        continue
    
    # Regular paragraph — handle image references by splitting text
    full_text = block.replace('\n', '')
    
    # Split on markdown image syntax: ![图N](path)
    parts = re.split(r'(!\[(图\d+)\]\(([^)]+)\))', full_text)
    
    para_content = []
    for i, part in enumerate(parts):
        if not part:
            continue
        m = re.match(r'!\[(图\d+)\]\(([^)]+)\)', part)
        if m:
            label = m.group(1)
            img_path = m.group(2)
            para_content.append(f'<span class="img-ref" data-img="{img_path}" data-label="{label}">🖼 {label}</span>')
        else:
            para_content.append(escape(part))
    
    combined = ''.join(para_content)
    if combined.strip():
        body_parts.append(f'<span class="para" id="para-{para_id:04d}"><span class="para" id="para-{para_id:04d}"><span class="para" id="para-{para_id:04d}">{combined}</span></span></span>')
        para_id += 1

body_html = '\n'.join(body_parts)

toc_html = ''
for lv, title, hid in toc_items:
    cls = 'toc-h2' if lv == 1 else ('toc-h3' if lv == 2 else 'toc-h4')
    toc_html += f'<li class="toc-item {cls}"><a href="#{hid}">{escape(title)}</a></li>\n'

SIDEBAR = '''<li><a href="01_史记_天官书第五.html"><span class="ch-num">01</span><span class="ch-book">史记</span><span class="ch-name">天官书</span></a></li>
<li><a href="02_汉书_天文志.html"><span class="ch-num">02</span><span class="ch-book">汉书</span><span class="ch-name">天文志</span></a></li>
<li><a href="03_后汉书_天文志.html"><span class="ch-num">03</span><span class="ch-book">后汉书</span><span class="ch-name">天文志</span></a></li>
<li><a href="04_晋书_天文志.html"><span class="ch-num">04</span><span class="ch-book">晋书</span><span class="ch-name">天文志</span></a></li>
<li><a href="05_宋书_天文志.html"><span class="ch-num">05</span><span class="ch-book">宋书</span><span class="ch-name">天文志</span></a></li>
<li><a href="06_南齐书_天文志.html"><span class="ch-num">06</span><span class="ch-book">南齐书</span><span class="ch-name">天文志</span></a></li>
<li><a href="07_魏书_天象志.html"><span class="ch-num">07</span><span class="ch-book">魏书</span><span class="ch-name">天象志</span></a></li>
<li><a href="08_隋书_天文志.html"><span class="ch-num">08</span><span class="ch-book">隋书</span><span class="ch-name">天文志</span></a></li>
<li><a href="09_旧唐书_天文志.html"><span class="ch-num">09</span><span class="ch-book">旧唐书</span><span class="ch-name">天文志</span></a></li>
<li><a href="10_新唐书_天文志.html"><span class="ch-num">10</span><span class="ch-book">新唐书</span><span class="ch-name">天文志</span></a></li>
<li><a href="11_旧五代史_天文志.html"><span class="ch-num">11</span><span class="ch-book">旧五代史</span><span class="ch-name">天文志</span></a></li>
<li><a href="12_新五代史_司天考.html"><span class="ch-num">12</span><span class="ch-book">新五代史</span><span class="ch-name">司天考</span></a></li>
<li><a href="13_宋史_天文志.html"><span class="ch-num">13</span><span class="ch-book">宋史</span><span class="ch-name">天文志</span></a></li>
<li><a href="14_辽史_历象志.html"><span class="ch-num">14</span><span class="ch-book">辽史</span><span class="ch-name">历象志</span></a></li>
<li><a href="15_金史_天文志.html"><span class="ch-num">15</span><span class="ch-book">金史</span><span class="ch-name">天文志</span></a></li>
<li><a href="16_元史_天文志.html"><span class="ch-num">16</span><span class="ch-book">元史</span><span class="ch-name">天文志</span></a></li>
<li><a href="17_明史_天文志.html"><span class="ch-num">17</span><span class="ch-book">明史</span><span class="ch-name">天文志</span></a></li>
<li><a href="18_步天歌.html"><span class="ch-num">18</span><span class="ch-book">步天歌</span><span class="ch-name">步天歌</span></a></li>
<li><a href="19_乙巳占.html"><span class="ch-num">19</span><span class="ch-book">乙巳占</span><span class="ch-name">乙巳占</span></a></li>
<li><a href="20_星庐中国古天文学概论.html"><span class="ch-num">20</span><span class="ch-book">星庐概论</span><span class="ch-name">中国古天文学概论</span></a></li>
<li><a href="21_开元占经.html"><span class="ch-num">21</span><span class="ch-book">开元占经</span><span class="ch-name">开元占经</span></a></li>
<li><a href="22_淮南子_天文训.html"><span class="ch-num">22</span><span class="ch-book">淮南子</span><span class="ch-name">天文训</span></a></li>
<li><a href="23_马王堆帛书_五星占.html"><span class="ch-num">23</span><span class="ch-book">马王堆帛书</span><span class="ch-name">五星占</span></a></li>
<li class="active"><a href="24_星庐_占星回廊.html"><span class="ch-num">24</span><span class="ch-book">占星回廊</span><span class="ch-name">天文占星学</span></a></li>'''

CSS = '''.img-ref { color: var(--accent-gold); cursor: pointer; border-bottom: 1px dotted var(--accent-gold); transition: font-size 0.25s ease, color 0.25s ease; margin: 0 4px; display: block; text-align: center; padding: 8px 0; }
.img-ref:hover { font-size: 1.15em; color: var(--accent-warm); }
.img-popup { position: fixed; z-index: 9999; right: 20px; top: 80px; max-width: 480px; max-height: 75vh; background: #141a2e; border: 1px solid var(--accent-gold); border-radius: 8px; box-shadow: 0 8px 32px rgba(0,0,0,0.7); padding: 10px; opacity: 0; pointer-events: none; visibility: hidden; transition: opacity 0.2s ease, visibility 0.2s ease; }
.img-popup.show { opacity: 1; visibility: visible; pointer-events: auto; }
.img-popup img { max-width: 100%; max-height: 70vh; display: block; border-radius: 4px; }
.img-popup .img-label { text-align: center; color: var(--text-muted); font-size: 0.8rem; margin-top: 6px; }
.poem-block { text-align: center; color: var(--accent-gold); font-family: var(--font-serif); font-size: 1.1rem; line-height: 2.2; margin: 20px 0; padding: 16px; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.toc-nav{background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:24px 28px;margin-bottom:32px}
.toc-title{font-family:var(--font-serif);font-size:1.15rem;font-weight:700;color:var(--accent-gold);padding-bottom:12px;margin-bottom:8px;border-bottom:1px solid var(--border);letter-spacing:0.15em;text-align:center}
.toc-list{list-style:none;padding:0;margin:0}
.toc-item{line-height:1.6}
.toc-item a{color:var(--text-body);text-decoration:none;display:block;padding:4px 0;font-size:0.95rem}
.toc-item a:hover{color:var(--accent-gold)}
.toc-h2 a{font-weight:600}
.toc-h3 a{padding-left:20px;font-size:0.88rem;color:var(--text-muted)}
.toc-h3 a::before{content:"└ ";color:var(--border-light)}
.toc-h4 a{padding-left:40px;font-size:0.82rem;color:var(--text-dim)}
.toc-h4 a::before{content:"└└ ";color:var(--border-light)}
.tips-box{background:rgba(201,169,110,0.08);border:1px solid rgba(201,169,110,0.2);border-radius:8px;padding:12px 18px;margin:12px 0;font-size:0.9rem;font-family:var(--font-sans)}
.tips-box strong{color:var(--accent-gold)}
.tips-box p{margin:6px 0 0;text-indent:0!important}'''

JS = '''(function(){var popup=document.getElementById('img-popup'),img=popup.querySelector('img'),label=popup.querySelector('.img-label'),cur=null;
document.addEventListener('mouseover',function(e){var r=e.target.closest('.img-ref');if(!r||r===cur)return;cur=r;var s=r.getAttribute('data-img'),l=r.getAttribute('data-label');if(s){img.src=s;label.textContent=l||'';popup.classList.add('show');}});
document.addEventListener('mouseout',function(e){var r=e.target.closest('.img-ref');if(r&&r.contains(e.relatedTarget))return;popup.classList.remove('show');cur=null;});})();'''

page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(TITLE)} - 星庐·中国古天文学知识库</title>
<link rel="stylesheet" href="../css/style.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&family=Noto+Sans+SC:wght@300;400;700&display=swap">
<script src="../js/anti-copy.js?v=5"></script>
<style>{CSS}</style></head>
<body>
<nav class="top-nav"><div class="nav-inner">
<a href="../index.html" class="nav-logo">&#9737; 星庐·中国古天文学知识库</a>
<div class="nav-links">
<a href="../index.html">首页</a><a href="../search.html">搜索</a>
<a href="../kg/timeline.html">天象事件</a><a href="../kg/starmap.html">古星图</a>
<a href="../kg/network.html">知识图谱</a>
<a href="https://github.com" target="_blank" class="nav-gh">GitHub</a>
<span class="nav-theme" style="color:var(--text-muted);margin-left:2px"><a id="theme-day" href="javascript:_switchTheme('light')" style="color:var(--text-muted);text-decoration:none">昼</a>/<a id="theme-night" href="javascript:_switchTheme('dark')" style="color:var(--accent-gold);text-decoration:none;font-weight:700">夜</a></span>
</div></nav>
<div class="chapter-container">
<aside class="chapter-sidebar"><h3>古天文典籍</h3><ul class="chapter-list">{SIDEBAR}</ul></aside>
<main class="chapter-content">
<div class="chapter-header">
<span class="chapter-dynasty">{escape(DYNASTY)}</span><h1>{escape(TITLE)}</h1>
<div class="chapter-meta"><span>作者：{escape(AUTHOR)}</span></div>
<p class="chapter-desc">{escape(DESC)}</p></div>
<nav class="toc-nav"><div class="toc-title">目 录</div><ul class="toc-list">{toc_html}</ul></nav>
<div class="chapter-body">{body_html}</div>
</main></div>
<div class="img-popup" id="img-popup"><img src="" alt=""><div class="img-label"></div></div>
<script src="../js/qr-popup.js"></script><script src="../js/theme.js"></script>
<script>{JS}</script>
</body></html>'''

with open(out_path, 'w', encoding='utf-8') as f:
    f.write(page)

# Verify no escaped tags in body
escaped_tags = re.findall(r'&lt;span class=&quot;img-ref&quot;', page)
print(f'Double-escaped tags: {len(escaped_tags)}')
print(f'File: {len(page)} bytes, {para_id-1} paragraphs, {len(toc_items)} TOC items')
