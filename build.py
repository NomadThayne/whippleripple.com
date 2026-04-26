#!/usr/bin/env python3
"""
WhippleRipple Build Script
==========================
Run this whenever you add or edit poems:

    python build.py

It will generate the output/ folder ready to upload to GitHub.
"""

import json
import os
import re
import shutil
from datetime import date

# ── Config ─────────────────────────────────────────────────────────────────
SITE_URL    = "https://whippleripple.com"
POEMS_FILE  = "poems.json"
TEMPLATE    = "template.html"
OUT_DIR     = "output"
POEMS_DIR   = os.path.join(OUT_DIR, "poems")

# ── Helpers ─────────────────────────────────────────────────────────────────
def slug(title):
    return re.sub(r'^-|-$', '', re.sub(r'[^a-z0-9]+', '-', title.lower()))

def format_date(d):
    # d is "YYYY-MM-DD"
    months = ['Jan','Feb','Mar','Apr','May','Jun',
              'Jul','Aug','Sep','Oct','Nov','Dec']
    y, m, day = d.split('-')
    return f"{months[int(m)-1]} {int(day)}, {y}"

def poem_url(poem):
    return f"{SITE_URL}/poems/{slug(poem['title'])}.html"

def excerpt(content, chars=300):
    text = content.replace('\\n', '\n')
    return text[:chars].rsplit('\n', 1)[0] + '…' if len(text) > chars else text

# ── Load data ────────────────────────────────────────────────────────────────
print("Loading poems...")
with open(POEMS_FILE, encoding='utf-8') as f:
    poems = json.load(f)
print(f"  {len(poems)} poems loaded")

# Sort by date ascending (oldest first) — matches site default
poems_sorted = sorted(poems, key=lambda p: p['date'])

# ── Prepare output dirs ──────────────────────────────────────────────────────
if os.path.exists(OUT_DIR):
    # Windows sometimes locks folders open in Explorer — retry with error handler
    def handle_remove_error(func, path, exc_info):
        import stat
        os.chmod(path, stat.S_IWRITE)
        func(path)
    shutil.rmtree(OUT_DIR, onexc=handle_remove_error)
os.makedirs(POEMS_DIR)

# ── 1. Build index.html ──────────────────────────────────────────────────────
print("Building index.html...")
with open(TEMPLATE, encoding='utf-8') as f:
    template = f.read()

poems_json = json.dumps(poems, ensure_ascii=False, separators=(',', ':'))
index_html = template.replace(
    'const POEMS = /*POEMS_DATA*/[]/*END_POEMS*/',
    f'const POEMS = {poems_json}'
)

# Inject SEO meta tags if not already present
if 'og:url' not in index_html:
    og = f'''
  <meta property="og:url" content="{SITE_URL}/">
  <meta property="og:type" content="website">'''
    index_html = index_html.replace('</head>', og + '\n</head>')

with open(os.path.join(OUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(index_html)
print("  output/index.html done")

# ── Copy commission.html ─────────────────────────────────────────────────────
print("Copying commission.html...")
shutil.copy('commission.html', os.path.join(OUT_DIR, 'commission.html'))
print("  output/commission.html done")

# ── 2. Build individual poem pages ───────────────────────────────────────────
print("Building poem pages...")

POEM_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Thayne Whipple</title>
<meta name="description" content="{excerpt}">
<meta name="author" content="Thayne Whipple">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title} — Thayne Whipple">
<meta property="og:description" content="{excerpt}">
<meta property="og:site_name" content="WhippleRipple">
<link rel="canonical" href="{url}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300;1,400&family=Josefin+Sans:wght@200;300;400&display=swap" rel="stylesheet">
<style>
  :root {{
    --ink: #1a1614; --paper: #f5f0e8; --cream: #ede7d6;
    --rust: #8b3a2a; --gold: #b8975a; --muted: #7a6e62; --line: #d4c9b5;
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:var(--paper); color:var(--ink); font-family:'Cormorant Garamond',Georgia,serif; min-height:100vh; }}
  header {{
    background:#0d1117; color:var(--paper); padding:1.5rem 2rem;
    display:flex; align-items:center; justify-content:space-between;
  }}
  .site-name {{
    font-family:'Cormorant Garamond',serif; font-size:1.8rem; font-weight:300;
    letter-spacing:0.08em; text-decoration:none; color:var(--paper);
  }}
  .site-name em {{ color:var(--gold); font-style:italic; }}
  .back-btn {{
    font-family:'Josefin Sans',sans-serif; font-size:0.7rem; letter-spacing:0.15em;
    text-transform:uppercase; color:var(--gold); text-decoration:none;
    border:1px solid rgba(184,151,90,0.4); padding:0.4rem 1rem;
    transition:all 0.2s;
  }}
  .back-btn:hover {{ background:rgba(184,151,90,0.1); border-color:var(--gold); }}
  .commission-btn {{
    font-family:'Josefin Sans',sans-serif; font-size:0.65rem; letter-spacing:0.15em;
    text-transform:uppercase; color:var(--gold); text-decoration:none;
    border:1px solid rgba(184,151,90,0.4); padding:0.4rem 1rem;
    transition:all 0.2s;
  }}
  .commission-btn:hover {{ background:rgba(184,151,90,0.1); }}
  main {{ max-width:680px; margin:4rem auto; padding:0 2rem 4rem; }}
  .poem-label {{
    font-family:'Josefin Sans',sans-serif; font-size:0.65rem; letter-spacing:0.3em;
    color:var(--gold); text-transform:uppercase; margin-bottom:0.5rem;
  }}
  h1 {{
    font-family:'Cormorant Garamond',serif; font-size:clamp(2rem,4vw,3rem);
    font-weight:300; line-height:1.2; margin-bottom:0.5rem;
  }}
  .poem-date {{
    font-family:'Josefin Sans',sans-serif; font-size:0.65rem; letter-spacing:0.2em;
    color:var(--muted); text-transform:uppercase; margin-bottom:2.5rem;
    padding-bottom:1.5rem; border-bottom:1px solid var(--line);
  }}
  .poem-body {{
    font-size:1.3rem; line-height:2; font-weight:300; white-space:pre-wrap;
  }}
  .poem-stanza {{ margin-bottom:1.5rem; }}
  .poem-author {{
    margin-top:3rem; font-family:'Josefin Sans',sans-serif; font-size:0.7rem;
    letter-spacing:0.25em; color:var(--rust); text-transform:uppercase;
  }}
  .read-more {{
    margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--line);
    text-align:center;
  }}
  .read-more p {{
    font-family:'Josefin Sans',sans-serif; font-size:0.75rem; letter-spacing:0.1em;
    color:var(--muted); margin-bottom:1rem;
  }}
  .read-more a {{
    font-family:'Josefin Sans',sans-serif; font-size:0.7rem; letter-spacing:0.15em;
    text-transform:uppercase; background:var(--rust); color:var(--paper);
    text-decoration:none; padding:0.6rem 1.4rem; display:inline-block;
    transition:opacity 0.2s;
  }}
  .read-more a:hover {{ opacity:0.85; }}
  footer {{
    background:var(--ink); color:var(--muted); text-align:center;
    padding:1.5rem; font-family:'Josefin Sans',sans-serif;
    font-size:0.65rem; letter-spacing:0.2em; text-transform:uppercase;
  }}
</style>
</head>
<body>
<header>
  <a class="site-name" href="/">Whipple<em>Ripple</em></a>
  <div style="display:flex;gap:1rem;align-items:center;">
    <a class="commission-btn" href="/commission.html">✦ Commission a Poem</a>
    <a class="back-btn" href="/{hash_link}">&#8592; All Poems</a>
  </div>
</header>
<main>
  <div class="poem-label">A Poem by Thayne Whipple</div>
  <h1>{title}</h1>
  <div class="poem-date">{date}</div>
  <div class="poem-body">{stanzas}</div>
  <div class="poem-author">— Thayne Whipple</div>
  <div class="read-more">
    <p>Discover 291 poems and writings by Thayne Whipple</p>
    <a href="/{hash_link}">Read More Poems &rsaquo;</a>
  </div>
</main>
<footer>&copy; Thayne Whipple &nbsp;&middot;&nbsp; WhippleRipple &nbsp;&middot;&nbsp; All rights reserved</footer>
</body>
</html>"""

for poem in poems:
    s = slug(poem['title'])
    content = poem['content'].replace('\\n', '\n')
    stanzas_html = '\n'.join(
        f'<div class="poem-stanza">{st.strip().replace(chr(10), "<br>")}</div>'
        for st in content.split('\n\n') if st.strip()
    )
    hash_link = f"#{s}"
    page = POEM_PAGE.format(
        title   = poem['title'],
        excerpt = excerpt(content, 200).replace('"', '&quot;'),
        url     = poem_url(poem),
        date    = format_date(poem['date']),
        stanzas = stanzas_html,
        hash_link = hash_link,
    )
    with open(os.path.join(POEMS_DIR, f"{s}.html"), 'w', encoding='utf-8') as f:
        f.write(page)

print(f"  {len(poems)} poem pages written to output/poems/")

# ── 3. Build sitemap.xml ─────────────────────────────────────────────────────
print("Building sitemap.xml...")
today = date.today().isoformat()

urls = [f"""  <url>
    <loc>{SITE_URL}/</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>""",
  f"""  <url>
    <loc>{SITE_URL}/commission.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>"""]

for poem in poems:
    urls.append(f"""  <url>
    <loc>{poem_url(poem)}</loc>
    <lastmod>{poem['date']}</lastmod>
    <changefreq>never</changefreq>
    <priority>0.7</priority>
  </url>""")

sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n'
sitemap += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
sitemap += '\n'.join(urls)
sitemap += '\n</urlset>\n'

with open(os.path.join(OUT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
    f.write(sitemap)
print("  output/sitemap.xml done")

# ── 4. Build robots.txt ──────────────────────────────────────────────────────
robots = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
with open(os.path.join(OUT_DIR, 'robots.txt'), 'w') as f:
    f.write(robots)
print("  output/robots.txt done")

# ── Summary ──────────────────────────────────────────────────────────────────
print()
print("=" * 50)
print(f"Build complete!")
print(f"  {len(poems)} poems")
print(f"  output/index.html")
print(f"  output/poems/  ({len(poems)} pages)")
print(f"  output/sitemap.xml")
print(f"  output/robots.txt")
print()
print("Upload the contents of output/ to GitHub.")
print("=" * 50)
