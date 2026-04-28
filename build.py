"""
Generates a single index.html from all campaign markdown files.
Run: python build.py
Then open: index.html
"""
import base64
import mimetypes
import re
import markdown
from pathlib import Path

BASE = Path(__file__).parent / "this-is-bullcrit"

SECTIONS = [
    ("Campaign State", [BASE / "campaign-state.md"]),
    ("Sessions", sorted(BASE.glob("sessions/*.md"), reverse=True)),
    ("Party", sorted(BASE.glob("party/*.md"))),
    ("NPCs", sorted(BASE.glob("npcs/*.md"))),
    ("Locations", sorted(BASE.glob("locations/*.md"))),
    ("Maps", sorted(BASE.glob("maps/*.md"))),
]

def slugify(path):
    rel = Path(path).relative_to(BASE)
    return str(rel).replace("\\", "/").replace("/", "-").replace(" ", "-").replace(".md", "")

def render_nav(sections):
    html = "<ul>"
    for section_name, files in sections:
        files = list(files)
        if not files:
            continue
        section_id = section_name.lower().replace(" ", "-")
        html += (
            f'<li class="section" id="sec-{section_id}">'
            f'<span class="section-label" onclick="toggleSection(\'{section_id}\')">'
            f'<span class="section-arrow">&#9660;</span>{section_name}'
            f'</span>'
            f'<ul class="section-items">'
        )
        for f in files:
            slug = slugify(f)
            title = f.stem.replace("-", " ").title()
            html += f'<li><a href="#{slug}" onclick="show(\'{slug}\'); return false;">{title}</a></li>'
        html += "</ul></li>"
    html += "</ul>"
    return html

def embed_images(html, md_file_dir):
    def replace_src(m):
        src = m.group(1)
        if src.startswith("http"):
            return m.group(0)
        img_path = (md_file_dir / src).resolve()
        if img_path.exists():
            mime = mimetypes.guess_type(str(img_path))[0] or "image/png"
            data = base64.b64encode(img_path.read_bytes()).decode()
            return f'src="data:{mime};base64,{data}"'
        return m.group(0)
    return re.sub(r'src="([^"]+)"', replace_src, html)

def render_pages(sections):
    md = markdown.Markdown(extensions=["tables", "fenced_code", "pymdownx.tilde"])
    pages = {}
    for _, files in sections:
        for f in list(files):
            slug = slugify(f)
            text = f.read_text(encoding="utf-8")
            md.reset()
            rendered = md.convert(text)
            pages[slug] = embed_images(rendered, f.parent)
    return pages

nav_html = render_nav(SECTIONS)
pages = render_pages(SECTIONS)

pages_js = "const pages = {\n"
for slug, content in pages.items():
    escaped = content.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    pages_js += f'  "{slug}": `{escaped}`,\n'
pages_js += "};"

first_slug = next(iter(pages))

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }

@keyframes flicker {
  0%, 89%, 94%, 100% { opacity: 1; }
  90%  { opacity: 0.80; }
  91%  { opacity: 0.97; }
  92%  { opacity: 0.75; }
  93%  { opacity: 0.98; }
}

@keyframes emberRise {
  0%   { transform: translateY(0)     translateX(0)                        scale(1);    opacity: 0.9; }
  50%  { transform: translateY(-38vh) translateX(var(--drift))             scale(0.55); opacity: 0.45; }
  100% { transform: translateY(-76vh) translateX(calc(var(--drift) * 1.8)) scale(0.1);  opacity: 0; }
}

@keyframes contentFade {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

html, body { height: 100%; overflow: hidden; }

body {
  font-family: 'IM Fell English', Georgia, serif;
  background: #06040200;
  color: #e8dcc0;
  display: flex;
  height: 100vh;
  overflow: hidden;
  position: relative;
}

/* Dungeon hallway background */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url('https://images.unsplash.com/photo-1576659182778-0efca7333177?w=1920&q=80');
  background-size: cover;
  background-position: center 40%;
  opacity: 0.42;
  z-index: 0;
  pointer-events: none;
}

/* Vignette */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background: radial-gradient(ellipse at 55% 45%, transparent 15%, rgba(3, 2, 1, 0.88) 100%);
  z-index: 1;
  pointer-events: none;
}

/* Floating embers */
.embers {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 2;
  overflow: hidden;
}

.ember {
  position: absolute;
  bottom: -4px;
  width: 2px;
  height: 2px;
  border-radius: 50%;
  background: radial-gradient(circle, #ffc040 0%, #ff6010 65%, transparent 100%);
  box-shadow: 0 0 5px 2px rgba(255, 150, 20, 0.65);
  animation: emberRise var(--duration) ease-in var(--delay) infinite;
  left: var(--x);
}

/* ── Nav ──────────────────────────────────────────────────────────────── */

nav {
  position: relative;
  z-index: 10;
  width: 268px;
  min-width: 268px;
  background: linear-gradient(175deg, rgba(10, 7, 3, 0.98) 0%, rgba(15, 10, 4, 0.96) 100%);
  overflow-y: auto;
  overflow-x: hidden;
  border-right: 1px solid rgba(180, 130, 40, 0.22);
  box-shadow: 4px 0 32px rgba(0, 0, 0, 0.75), inset -1px 0 0 rgba(180, 130, 40, 0.07);
  scrollbar-width: thin;
  scrollbar-color: rgba(180, 130, 40, 0.22) transparent;
  animation: flicker 14s ease-in-out infinite;
  transition: width 0.28s ease, min-width 0.28s ease, border-color 0.28s ease;
}

nav.nav-collapsed {
  width: 0;
  min-width: 0;
  border-right-color: transparent;
  overflow: hidden;
}

.sidebar-toggle {
  position: fixed;
  left: 268px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 15;
  width: 16px;
  height: 48px;
  background: rgba(12, 8, 3, 0.97);
  border: 1px solid rgba(180, 130, 40, 0.28);
  border-left: none;
  border-radius: 0 4px 4px 0;
  color: rgba(180, 130, 40, 0.6);
  cursor: pointer;
  font-size: 0.9em;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: left 0.28s ease, color 0.15s ease;
  padding: 0;
  line-height: 1;
  user-select: none;
}

.sidebar-toggle:hover { color: #f0d080; }

.sidebar-toggle.nav-collapsed {
  left: 0;
  border-left: 1px solid rgba(180, 130, 40, 0.28);
  border-right: none;
  border-radius: 4px 0 0 4px;
}

/* Faint stone texture behind nav */
nav::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url('https://images.unsplash.com/photo-1576659182778-0efca7333177?w=500&q=30');
  background-size: cover;
  background-position: left center;
  opacity: 0.05;
  pointer-events: none;
}

.nav-header {
  padding: 32px 20px 20px;
  text-align: center;
  position: relative;
  border-bottom: 1px solid rgba(180, 130, 40, 0.14);
  margin-bottom: 6px;
}

.nav-title {
  font-family: 'Cinzel Decorative', serif;
  color: #c9a040;
  font-size: 1.02em;
  font-weight: 700;
  line-height: 1.35;
  text-shadow: 0 0 28px rgba(201, 160, 64, 0.4), 0 2px 8px rgba(0, 0, 0, 0.9);
  letter-spacing: 1px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.nav-sword {
  color: rgba(201, 160, 64, 0.5);
  font-size: 1.05em;
  display: inline-block;
}

.nav-subtitle {
  font-family: 'Cinzel', serif;
  color: rgba(180, 140, 80, 0.4);
  font-size: 0.57em;
  letter-spacing: 4px;
  text-transform: uppercase;
  margin-top: 8px;
}

nav ul { list-style: none; padding-bottom: 28px; }

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 16px 20px 4px;
  color: rgba(180, 130, 40, 0.45);
  font-family: 'Cinzel', serif;
  font-size: 0.58em;
  letter-spacing: 3px;
  text-transform: uppercase;
  cursor: pointer;
  user-select: none;
  transition: color 0.15s ease;
}

.section-label:hover { color: rgba(180, 130, 40, 0.7); }

.section-label::after {
  content: '';
  display: block;
  flex: 1;
  height: 1px;
  margin-top: 0;
  background: linear-gradient(to right, rgba(180, 130, 40, 0.22), transparent 70%);
}

.section-arrow {
  font-size: 0.75em;
  transition: transform 0.22s ease;
  display: inline-block;
  line-height: 1;
  color: rgba(180, 130, 40, 0.5);
}

.section.collapsed .section-arrow { transform: rotate(-90deg); }

.section-items {
  overflow: hidden;
  max-height: 600px;
  transition: max-height 0.28s ease, opacity 0.22s ease;
  opacity: 1;
}

.section.collapsed .section-items {
  max-height: 0;
  opacity: 0;
}

nav li.section ul li a {
  display: block;
  padding: 5px 20px 5px 28px;
  color: #a8906a;
  text-decoration: none;
  font-family: 'IM Fell English', serif;
  font-size: 0.9em;
  border-left: 2px solid transparent;
  transition: color 0.18s ease, border-color 0.18s ease, background 0.18s ease, padding-left 0.14s ease;
  position: relative;
  line-height: 1.45;
}

nav li.section ul li a::before {
  content: '›';
  position: absolute;
  left: 15px;
  color: rgba(180, 130, 40, 0.22);
  transition: color 0.18s ease, left 0.14s ease;
}

nav li.section ul li a:hover,
nav li.section ul li a.active {
  color: #f0d880;
  border-left-color: #c9a040;
  background: linear-gradient(to right, rgba(180, 130, 40, 0.1), transparent 75%);
  text-shadow: 0 0 16px rgba(240, 200, 80, 0.32);
  padding-left: 32px;
}

nav li.section ul li a:hover::before,
nav li.section ul li a.active::before {
  color: #c9a040;
  left: 17px;
}

/* ── Main ─────────────────────────────────────────────────────────────── */

main {
  position: relative;
  z-index: 10;
  flex: 1;
  overflow-y: auto;
  padding: 52px 72px 64px;
  background: rgba(10, 7, 3, 0.84);
  backdrop-filter: blur(3px);
  scrollbar-width: thin;
  scrollbar-color: rgba(180, 130, 40, 0.22) transparent;
}

/* Top-right gold corner ornament */
main::after {
  content: '';
  position: fixed;
  top: 18px;
  right: 18px;
  width: 52px;
  height: 52px;
  border-top: 1px solid rgba(180, 130, 40, 0.35);
  border-right: 1px solid rgba(180, 130, 40, 0.35);
  pointer-events: none;
  z-index: 20;
}

#content {
  max-width: 820px;
  animation: contentFade 0.38s ease forwards;
  display: flow-root;
}

main h1 {
  font-family: 'Cinzel', serif;
  color: #d4a840;
  font-size: 1.9em;
  font-weight: 600;
  margin-bottom: 0;
  text-shadow: 0 0 40px rgba(212, 168, 64, 0.22);
  letter-spacing: 1px;
}

main h1::after {
  content: '';
  display: block;
  height: 1px;
  background: linear-gradient(to right, rgba(180, 130, 40, 0.5), rgba(180, 130, 40, 0.12), transparent);
  margin-top: 12px;
  margin-bottom: 24px;
}

main h2 {
  font-family: 'Cinzel', serif;
  color: #b08030;
  font-size: 1.25em;
  font-weight: 600;
  margin: 34px 0 10px;
  letter-spacing: 0.4px;
}

main h3 {
  font-family: 'Cinzel', serif;
  color: #907020;
  font-size: 1.05em;
  margin: 24px 0 8px;
}

main h4 {
  font-family: 'Cinzel', serif;
  color: #806018;
  font-size: 0.95em;
  margin: 18px 0 6px;
}

main p {
  line-height: 1.9;
  margin-bottom: 14px;
}

main ul, main ol {
  margin: 6px 0 14px 26px;
  line-height: 1.8;
}

main li { margin-bottom: 5px; }

main li::marker { color: rgba(180, 130, 40, 0.42); }

main strong { color: #d4b870; font-weight: normal; }

main em { color: #a09070; font-style: italic; }

main a {
  color: #c9a040;
  text-decoration: none;
  border-bottom: 1px solid rgba(201, 160, 64, 0.28);
  transition: color 0.15s, border-color 0.15s;
}
main a:hover { color: #f0d080; border-bottom-color: rgba(240, 208, 128, 0.55); }

main table {
  border-collapse: collapse;
  width: 100%;
  margin: 18px 0;
  border: 1px solid rgba(180, 130, 40, 0.16);
}

main th {
  background: rgba(180, 130, 40, 0.09);
  color: #c9a040;
  padding: 9px 14px;
  text-align: left;
  border: 1px solid rgba(180, 130, 40, 0.16);
  font-family: 'Cinzel', serif;
  font-size: 0.82em;
  letter-spacing: 0.4px;
  font-weight: 600;
}

main td {
  padding: 7px 14px;
  border: 1px solid rgba(180, 130, 40, 0.09);
}

main tr:nth-child(even) { background: rgba(180, 130, 40, 0.04); }

main code {
  background: rgba(8, 5, 2, 0.65);
  padding: 2px 7px;
  border-radius: 3px;
  font-size: 0.87em;
  color: #80b890;
  border: 1px solid rgba(80, 60, 20, 0.26);
  font-family: monospace;
}

main pre {
  background: rgba(6, 4, 2, 0.78);
  padding: 18px 20px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 14px 0;
  border: 1px solid rgba(80, 60, 20, 0.2);
}

main pre code { padding: 0; border: none; background: none; }

main del { color: #504030; }

main img {
  max-width: 100%;
  border-radius: 5px;
  border: 1px solid rgba(180, 130, 40, 0.2);
  box-shadow: 0 6px 28px rgba(0, 0, 0, 0.6);
  display: block;
  margin: 10px 0;
}

/* Portrait images sit as the very first element (before h1), float right */
#content > p:first-child > img {
  max-width: 220px;
  float: right;
  margin: 0 0 20px 28px;
}


main hr {
  border: none;
  border-top: 1px solid rgba(180, 130, 40, 0.18);
  margin: 26px 0;
}

main blockquote {
  border-left: 2px solid rgba(180, 130, 40, 0.38);
  padding: 8px 20px;
  color: #907858;
  margin: 14px 0;
  background: rgba(180, 130, 40, 0.04);
  font-style: italic;
}

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(180, 130, 40, 0.26); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(180, 130, 40, 0.46); }
"""

# ---------------------------------------------------------------------------
# JS
# ---------------------------------------------------------------------------

JS_EMBERS = """
(function() {
  var container = document.getElementById('embers');
  for (var i = 0; i < 24; i++) {
    var e = document.createElement('div');
    e.className = 'ember';
    e.style.setProperty('--x', (Math.random() * 100) + '%');
    e.style.setProperty('--duration', (5 + Math.random() * 10) + 's');
    e.style.setProperty('--delay', (Math.random() * 12) + 's');
    e.style.setProperty('--drift', ((Math.random() - 0.5) * 90) + 'px');
    container.appendChild(e);
  }
})();
"""

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>This Is Bullcrit — Campaign Chronicle</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700&family=Cinzel:wght@400;600;700&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>
<div class="embers" id="embers"></div>
<nav>
  <div class="nav-header">
    <div class="nav-title">
      <span class="nav-sword">&#9876;</span>
      <a href="#" onclick="show('{first_slug}'); history.replaceState(null, '', location.pathname); return false;" style="color:inherit;text-decoration:none;border:none;cursor:pointer;">This Is<br>Bullcrit</a>
      <span class="nav-sword">&#9876;</span>
    </div>
    <div class="nav-subtitle">Campaign Chronicle</div>
  </div>
  {nav_html}
</nav>
<button class="sidebar-toggle" id="sidebar-toggle" onclick="toggleSidebar()" title="Toggle sidebar">&#8249;</button>
<main id="main-scroll">
  <div id="content"></div>
</main>
<script>
{pages_js}

{JS_EMBERS}

function toggleSection(id) {{
  var sec = document.getElementById('sec-' + id);
  if (!sec) return;
  var collapsed = sec.classList.toggle('collapsed');
  try {{
    var state = JSON.parse(localStorage.getItem('navCollapsed') || '{{}}');
    state[id] = collapsed;
    localStorage.setItem('navCollapsed', JSON.stringify(state));
  }} catch(e) {{}}
}}

function restoreSections() {{
  try {{
    var state = JSON.parse(localStorage.getItem('navCollapsed') || '{{}}');
    Object.keys(state).forEach(function(id) {{
      if (state[id]) {{
        var sec = document.getElementById('sec-' + id);
        if (sec) sec.classList.add('collapsed');
      }}
    }});
  }} catch(e) {{}}
}}

restoreSections();

function toggleSidebar() {{
  var nav = document.querySelector('nav');
  var btn = document.getElementById('sidebar-toggle');
  var collapsed = nav.classList.toggle('nav-collapsed');
  btn.classList.toggle('nav-collapsed', collapsed);
  btn.innerHTML = collapsed ? '&#8250;' : '&#8249;';
  try {{ localStorage.setItem('sidebarCollapsed', collapsed ? '1' : '0'); }} catch(e) {{}}
}}

(function() {{
  try {{
    if (localStorage.getItem('sidebarCollapsed') === '1') {{
      var nav = document.querySelector('nav');
      var btn = document.getElementById('sidebar-toggle');
      nav.classList.add('nav-collapsed');
      btn.classList.add('nav-collapsed');
      btn.innerHTML = '&#8250;';
      btn.style.left = '0';
    }}
  }} catch(e) {{}}
}})();

function show(slug) {{
  var content = document.getElementById('content');
  content.style.animation = 'none';
  void content.offsetHeight;
  content.style.animation = '';
  content.innerHTML = pages[slug] || '<p style="color:#666;font-style:italic">Not found.</p>';
  document.getElementById('main-scroll').scrollTop = 0;
  document.querySelectorAll('nav a').forEach(function(a) {{ a.classList.remove('active'); }});
  var link = document.querySelector('nav a[onclick="show(\\'' + slug + '\\')"]');
  if (link) link.classList.add('active');
  window.location.hash = slug;
}}

var hash = window.location.hash.slice(1);
show(hash && pages[hash] ? hash : "{first_slug}");
</script>
</body>
</html>
"""

out = Path(__file__).parent / "index.html"
out.write_text(html, encoding="utf-8")
print(f"Built: {out}")
