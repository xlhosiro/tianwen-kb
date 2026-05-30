#!/usr/bin/env python3
"""
tianwen-kb 静态站点生成器
将 D:\24history\twz\ 下的 Markdown 天文志文件渲染为 HTML 站点
"""

import os, re, json, shutil
from pathlib import Path

# ============ 配置 ============
PROJECT_ROOT = Path(r"D:\24history\twz\tianwen-kb")
CORPUS_MD = Path(r"D:\24history\twz")  # Markdown files location
DOCS_DIR = PROJECT_ROOT / "docs"
CHAPTERS_DIR = DOCS_DIR / "chapters"
DATA_DIR = DOCS_DIR / "data"

# 天文志元数据
CHAPTERS_META = [
    {"id": "01", "file": "01_史记_天官书.md", "book": "史记", "chapter": "天官书第五",
     "dynasty": "西汉", "author": "司马迁", "year": "约前91年", "volumes": 1,
     "desc": "中国现存最早的系统性天文学著作。将全天星官分为五宫（中东南西北），记录约90多个星官、500余颗恒星，叙述五星运行规律。"},
    {"id": "02", "file": "02_汉书_天文志.md", "book": "汉书", "chapter": "天文志",
     "dynasty": "东汉", "author": "班固", "year": "82年", "volumes": 1,
     "desc": "沿用史记天官书体系，补充汉代天象记录，含太阳黑子早期观测、分野学说。"},
    {"id": "03", "file": "03_后汉书_天文志.md", "book": "后汉书", "chapter": "天文志",
     "dynasty": "南朝宋", "author": "范晔/司马彪", "year": "445年", "volumes": 3,
     "desc": "司马彪续汉书八志之一。记载东汉天象，含著名的公元185年超新星记录（SN 185）。"},
    {"id": "04", "file": "04_晋书_天文志.md", "book": "晋书", "chapter": "天文志",
     "dynasty": "唐", "author": "房玄龄等/李淳风", "year": "648年", "volumes": 3,
     "desc": "李淳风撰写，体系完整。介绍盖天说、浑天说、宣夜说，详述浑天仪，载283官1464星。"},
    {"id": "05", "file": "05_宋书_天文志.md", "book": "宋书", "chapter": "天文志",
     "dynasty": "南朝梁", "author": "沈约", "year": "488年", "volumes": 4,
     "desc": "记录南朝刘宋天象，追述三国西晋天象以补前史之缺。"},
    {"id": "06", "file": "06_南齐书_天文志.md", "book": "南齐书", "chapter": "天文志",
     "dynasty": "南朝梁", "author": "萧子显", "year": "537年", "volumes": 2,
     "desc": "记录南齐（479-502年）天象，含日食、星变、分野占验。"},
    {"id": "07", "file": "07_魏书_天象志.md", "book": "魏书", "chapter": "天象志",
     "dynasty": "北齐", "author": "魏收", "year": "554年", "volumes": 4,
     "desc": "记录北魏时期（386-550年）天象，含日食、月食、五星、彗星、流星，按年月日排序。"},
    {"id": "08", "file": "08_隋书_天文志.md", "book": "隋书", "chapter": "天文志",
     "dynasty": "唐", "author": "魏徵等/李淳风", "year": "636年", "volumes": 3,
     "desc": "李淳风续作。天文学理论和仪器部分极为详尽，记载浑天仪、浑象、漏刻，三分法宇宙理论。"},
    {"id": "09", "file": "09_旧唐书_天文志.md", "book": "旧唐书", "chapter": "天文志",
     "dynasty": "后晋", "author": "刘昫等", "year": "945年", "volumes": 2,
     "desc": "记录唐代天象，含僧一行的天文学贡献、浑天仪、黄道游仪等仪器。"},
    {"id": "10", "file": "10_新唐书_天文志.md", "book": "新唐书", "chapter": "天文志",
     "dynasty": "宋", "author": "欧阳修、宋祁等", "year": "1060年", "volumes": 3,
     "desc": "与旧唐书互补，更重天文学理论。记录一行的大地测量工作，详载天文仪器和历法。"},
    {"id": "11", "file": "11_旧五代史_天文志.md", "book": "旧五代史", "chapter": "天文志",
     "dynasty": "宋", "author": "薛居正等", "year": "974年", "volumes": 1,
     "desc": "记录五代时期（907-960年）天象，以日食、彗星、星变为主要内容。"},
    {"id": "12", "file": "12_新五代史_司天考.md", "book": "新五代史", "chapter": "司天考",
     "dynasty": "宋", "author": "欧阳修", "year": "1053年", "volumes": 2,
     "desc": "偏重天文学理论探讨，讨论天人关系、灾异学说，记录五代天象。"},
    {"id": "13", "file": "13_宋史_天文志.md", "book": "宋史", "chapter": "天文志",
     "dynasty": "元", "author": "脱脱等", "year": "1345年", "volumes": 13,
     "desc": "二十四史中篇幅最大的天文志（13卷）。记录北宋南宋320年天象，含1054年超新星（蟹状星云），记载苏颂水运仪象台。"},
    {"id": "14", "file": "14_辽史_历象志.md", "book": "辽史", "chapter": "历象志",
     "dynasty": "元", "author": "脱脱等", "year": "1344年", "volumes": 3,
     "desc": "记录辽代（907-1125年）天文历法，含日食等天象。"},
    {"id": "15", "file": "15_金史_天文志.md", "book": "金史", "chapter": "天文志",
     "dynasty": "元", "author": "脱脱等", "year": "1345年", "volumes": 1,
     "desc": "记录金代（1115-1234年）天象，含日食、月食、星变等。"},
    {"id": "16", "file": "16_元史_天文志.md", "book": "元史", "chapter": "天文志",
     "dynasty": "明", "author": "宋濂等", "year": "1370年", "volumes": 2,
     "desc": "记载郭守敬的天文仪器（简仪、仰仪等），介绍西域天文学传入，记载札马鲁丁的西域天文仪器。"},
    {"id": "17", "file": "17_明史_天文志.md", "book": "明史", "chapter": "天文志",
     "dynasty": "清", "author": "张廷玉等", "year": "1739年", "volumes": 3,
     "desc": "二十四史最后一部天文志。介绍利玛窦带来的西方天文学，记载徐光启与崇祯历书，反映中西天文学融合。"},
]


# ============ 星官颜色映射 ============
# 核心星官保持统一颜色，跨文献一致
CONSTELLATION_COLORS = {
    # 三垣
    "紫微垣": "#C9A96E", "紫宮": "#C9A96E", "紫微宮": "#C9A96E",
    "太微垣": "#D4A574", "太微": "#D4A574", "太微宮": "#D4A574",
    "天市垣": "#B8956A", "天市": "#B8956A",
    # 二十八宿 - 东方青龙
    "角宿": "#4A9B8E", "角": "#4A9B8E",
    "亢宿": "#5BA89A", "亢": "#5BA89A",
    "氐宿": "#6CB5A6", "氐": "#6CB5A6",
    "房宿": "#7DC2B2", "房": "#7DC2B2",
    "心宿": "#8ECFBE", "心": "#8ECFBE",
    "尾宿": "#9FDCCA", "尾": "#9FDCCA",
    "箕宿": "#B0E9D6", "箕": "#B0E9D6",
    # 二十八宿 - 北方玄武
    "斗宿": "#6B8DB5", "斗": "#6B8DB5", "南斗": "#6B8DB5",
    "牛宿": "#7B9DC5", "牛": "#7B9DC5",
    "女宿": "#8BADD5", "女": "#8BADD5",
    "虚宿": "#9BBDE5", "虚": "#9BBDE5",
    "危宿": "#ABCDF5", "危": "#ABCDF5",
    "室宿": "#5C7EA5", "室": "#5C7EA5", "營室": "#5C7EA5",
    "壁宿": "#6C8EB5", "壁": "#6C8EB5",
    # 二十八宿 - 西方白虎
    "奎宿": "#C4A35A", "奎": "#C4A35A",
    "婁宿": "#D4B36A", "婁": "#D4B36A",
    "胃宿": "#E4C37A", "胃": "#E4C37A",
    "昴宿": "#D4A35A", "昴": "#D4A35A",
    "畢宿": "#C4934A", "畢": "#C4934A",
    "觜宿": "#B4833A", "觜": "#B4833A",
    "參宿": "#E4B36A", "參": "#E4B36A",
    # 二十八宿 - 南方朱雀
    "井宿": "#C46B5A", "井": "#C46B5A", "東井": "#C46B5A",
    "鬼宿": "#D47B6A", "鬼": "#D47B6A", "輿鬼": "#D47B6A",
    "柳宿": "#E48B7A", "柳": "#E48B7A",
    "星宿": "#F49B8A", "星": "#F49B8A", "七星": "#F49B8A",
    "張宿": "#E47B6A", "張": "#E47B6A",
    "翼宿": "#D46B5A", "翼": "#D46B5A",
    "軫宿": "#C45B4A", "軫": "#C45B4A",
    # 重要恒星与星官
    "北斗": "#FFD700", "北斗七星": "#FFD700",
    "北極": "#FFD700", "北極星": "#FFD700", "北辰": "#FFD700",
    "太一": "#FFE44D", "天一": "#FFE44D",
    "文昌": "#E8C84A", "文昌宮": "#E8C84A",
    "三台": "#D4B84A", "三能": "#D4B84A",
    "軒轅": "#E8A84A",
    "攝提": "#C4C84A",
    "招搖": "#B4E84A",
    "天關": "#C8A84A",
    "天槍": "#A0C0D0", "天棓": "#A0C0D0",
    "閣道": "#90B0C0",
    "貫索": "#D0A0A0",
    "天駟": "#C0A060",
    "咸池": "#A0B0D0", "五車": "#A0B0D0",
    "南門": "#B0C0A0",
    "天庫": "#C0A080", "天庫樓": "#C0A080",
    "少微": "#A0C0C0",
    "郎位": "#C0C0A0", "郎將": "#C0C0A0",
    "騎官": "#B0B0C0",
    "積屍": "#C06060",
    "天街": "#C0B080",
    "天倉": "#C0A080",
    "天苑": "#A0B080",
    # 行星 (五星)
    "歲星": "#4CAF50", "木星": "#4CAF50",
    "熒惑": "#F44336", "火星": "#F44336",
    "鎮星": "#FF9800", "土星": "#FF9800", "塡星": "#FF9800",
    "太白": "#FFFFFF", "金星": "#E0E0E0",
    "辰星": "#2196F3", "水星": "#2196F3",
}


# ============ HTML 模板 ============
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 古天文知识库</title>
    <link rel="stylesheet" href="../css/style.css">
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&family=Noto+Sans+SC:wght@300;400;700&display=swap">
</head>
<body>
    <nav class="top-nav">
        <div class="nav-inner">
            <a href="../index.html" class="nav-logo">&#9737; 古天文知识库</a>
            <div class="nav-links">
                <a href="../index.html">首页</a>
                <a href="../search.html">搜索</a>
                <a href="../kg/timeline.html">时间线</a>
                <a href="../kg/starmap.html">古星图</a>
                <a href="../kg/network.html">关系网络</a>
                <a href="https://github.com" target="_blank" class="nav-gh">GitHub</a>
            </div>
        </div>
    </nav>

    <div class="chapter-container">
        <aside class="chapter-sidebar">
            <h3>二十四史天文志</h3>
            <ul class="chapter-list">
                {sidebar_links}
            </ul>
        </aside>

        <main class="chapter-content">
            <div class="chapter-header">
                <span class="chapter-dynasty">{dynasty}</span>
                <h1>{book} · {chapter_name}</h1>
                <div class="chapter-meta">
                    <span>作者：{author}</span>
                    <span>成书：{year}</span>
                    <span>卷数：{volumes}卷</span>
                </div>
                <p class="chapter-desc">{description}</p>
            </div>

            <div class="chapter-body">
                {body_html}
            </div>
        </main>
    </div>

    <footer>
        <p>古天文知识库 (tianwen-kb) — 基于二十四史天文志古籍原文构建</p>
    </footer>

    <script src="../js/chapter.js"></script>
</body>
</html>'''


def md_to_html(md_text, chapter_id):
    """Convert Markdown to HTML with star/constellation highlighting"""
    lines = md_text.split('\n')
    html_parts = []
    in_paragraph = False
    para_lines = []
    
    def flush_paragraph():
        nonlocal in_paragraph, para_lines
        if para_lines:
            text = ' '.join(para_lines)
            text = highlight_entities(text)
            html_parts.append(f'<p>{text}</p>')
            para_lines = []
            in_paragraph = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty lines
        if not stripped:
            flush_paragraph()
            continue
        
        # Headers
        if stripped.startswith('### '):
            flush_paragraph()
            text = stripped[4:]
            html_parts.append(f'<h3>{text}</h3>')
            continue
        elif stripped.startswith('## '):
            flush_paragraph()
            text = stripped[3:]
            html_parts.append(f'<h2>{text}</h2>')
            continue
        elif stripped.startswith('# '):
            flush_paragraph()
            text = stripped[2:]
            html_parts.append(f'<h1>{text}</h1>')
            continue
        elif stripped.startswith('> '):
            flush_paragraph()
            text = stripped[2:]
            html_parts.append(f'<blockquote>{text}</blockquote>')
            continue
        elif stripped.startswith('#### '):
            flush_paragraph()
            text = stripped[5:]
            html_parts.append(f'<h4>{text}</h4>')
            continue
        
        # Regular text
        para_lines.append(stripped)
        in_paragraph = True
    
    flush_paragraph()
    return '\n'.join(html_parts)


def highlight_entities(text):
    """Highlight star names, constellation names, and astronomical terms with color-coded spans"""
    # Sort by length descending to match longer names first
    sorted_terms = sorted(CONSTELLATION_COLORS.keys(), key=len, reverse=True)
    
    for term in sorted_terms:
        color = CONSTELLATION_COLORS[term]
        escaped = re.escape(term)
        # Simple replacement: wrap term in colored span
        # Avoid matching inside HTML tags by splitting on tags and only replacing in text segments
        parts = re.split(r'(<[^>]+>)', text)
        for i in range(0, len(parts), 2):  # Even indices are text, odd are tags
            if i < len(parts):
                replacement = f'<span class="astro-entity" style="color:{color};border-bottom:1px dotted {color}88;" title="{term}">{term}</span>'
                parts[i] = re.sub(f'({escaped})', replacement, parts[i])
        text = ''.join(parts)
    
    # Highlight annotations
    text = re.sub(r'【(索隱|正義|集解)】', r'<span class="annotation-label">【\1】</span>', text)
    
    return text


def build_sidebar_links(current_id):
    """Generate sidebar chapter navigation"""
    links = []
    for ch in CHAPTERS_META:
        active = ' class="active"' if ch['id'] == current_id else ''
        links.append(f'<li{active}><a href="{ch["id"]}_{ch["book"]}_{ch["chapter"].replace(" ", "")}.html">'
                     f'<span class="ch-num">{ch["id"]}</span>'
                     f'<span class="ch-book">{ch["book"]}</span>'
                     f'<span class="ch-name">{ch["chapter"]}</span>'
                     f'</a></li>')
    return '\n'.join(links)


def render_chapter(meta):
    """Render a single chapter HTML page"""
    md_path = CORPUS_MD / meta['file']
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    # Remove the first few lines (title + author, already in meta)
    lines = md_text.split('\n')
    # Skip title, author line, and any separator
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith('# ') or line.startswith('> '):
            continue
        if i > 1 and line.strip():
            body_start = i
            break
    body_text = '\n'.join(lines[body_start:])
    
    body_html = md_to_html(body_text, meta['id'])
    sidebar = build_sidebar_links(meta['id'])
    
    file_base = f"{meta['id']}_{meta['book']}_{meta['chapter'].replace(' ', '')}"
    filename = f"{file_base}.html"
    
    html = HTML_TEMPLATE.format(
        title=f"{meta['book']} · {meta['chapter']}",
        dynasty=meta['dynasty'],
        book=meta['book'],
        chapter_name=meta['chapter'],
        author=meta['author'],
        year=meta['year'],
        volumes=meta['volumes'],
        description=meta['desc'],
        sidebar_links=sidebar,
        body_html=body_html
    )
    
    output_path = CHAPTERS_DIR / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filename, len(html)


def main():
    print("=" * 60)
    print("  古天文知识库 静态站点生成器")
    print("=" * 60)
    
    # Ensure directories exist
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Render all chapters
    print("\n[1/3] 渲染章节页面...")
    chapter_files = []
    total_size = 0
    for meta in CHAPTERS_META:
        filename, size = render_chapter(meta)
        chapter_files.append((meta, filename))
        total_size += size
        print(f"  ✓ {filename} ({size:,} bytes)")
    
    print(f"\n  共 {len(CHAPTERS_META)} 个章节页面，总计 {total_size:,} bytes")
    
    # Save chapter metadata for index/search
    chapters_data = []
    for meta, filename in chapter_files:
        chapters_data.append({
            "id": meta["id"],
            "book": meta["book"],
            "chapter": meta["chapter"],
            "dynasty": meta["dynasty"],
            "author": meta["author"],
            "year": meta["year"],
            "volumes": meta["volumes"],
            "description": meta["desc"],
            "url": f"chapters/{filename}"
        })
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_DIR / "chapters.json", 'w', encoding='utf-8') as f:
        json.dump(chapters_data, f, ensure_ascii=False, indent=2)
    print(f"\n  ✓ 元数据已保存: docs/data/chapters.json")
    
    print(f"\n[DONE] 站点已生成到: {DOCS_DIR}")
    print(f"       用浏览器打开: {DOCS_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
