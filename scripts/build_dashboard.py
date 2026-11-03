"""Builds the live, interactive profile dashboard: dist/index.html (served by GitHub Pages from the output branch).

    python scripts/build_dashboard.py dist        # after build_github_stats.py has written dist/data.json

What the README cannot do, the dashboard does: hover cards on everything, a Bengaluru map card on the location,
per-day tooltips on the contribution matrix and per-week tooltips on the graph. One self-contained page: inline CSS
and JavaScript, no frameworks, no trackers. The Google map loads only when a visitor hovers or taps the location.
Text is inserted with textContent / escaped attributes, never as raw HTML from data.
"""

import html
import json
import re
import shutil
import sys
from pathlib import Path

import yaml

from svg_kit import ROOT


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def a(text):
    """Escape for an HTML attribute or text node."""
    return html.escape(str(text), quote=True)


def md_inline(text):
    """The few inline Markdown bits used in config (bold, links) -> safe HTML."""
    out = a(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    return re.sub(r"\[(.+?)\]\((https://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', out)


# where things sit on the 860 x 300 header and the 860 x 432 project diagram, for hover hotspots (x, y, w, h)
HERO_SPOTS = [
    ((46, 100, 300, 50), "Naman", "Data Engineer from Bengaluru, India."),
    (
        (46, 166, 160, 26),
        "Data Engineer",
        "Builds data platforms end to end: ingestion, modelling, quality, release, operations.",
    ),
    ((212, 164, 200, 30), "map", ""),
    ((46, 250, 300, 34), "Open to work", "Open to Data Engineering roles; immediate joiner."),
    (
        (612, 94, 184, 172),
        "Medallion layers",
        "Bronze keeps raw data, Silver cleans and checks it, Gold is ready for reporting.",
    ),
]
PROJECT_SPOTS = [
    (
        (28, 100, 150, 74),
        "Sources",
        "Synthetic files per environment on S3: CSV, pipe text, JSON, Excel CSV, a PDF bank statement and deposit-slip images (OCR).",
    ),
    (
        (28, 200, 150, 74),
        "Kafka",
        "Payment events streamed with Structured Streaming: watermark, de-duplication, 10-minute windows.",
    ),
    (
        (222, 140, 130, 94),
        "Bronze",
        "Auto Loader ingests every file as is; rejected files are logged, nothing is lost.",
    ),
    (
        (392, 140, 130, 94),
        "Silver",
        "Cleaning, SCD2 history, quarantine of bad rows and a quality checkpoint before Gold.",
    ),
    ((562, 140, 120, 94), "Gold", "Star schema written in SQL, one file per table; every invoice and loan reconciles."),
    ((718, 100, 116, 74), "Group view", "People matched across both companies; intercompany money counted once."),
    (
        (718, 200, 116, 74),
        "BI + alerts",
        "Dashboards with column masks and row filters per viewer; HTML alert mails, each finding once.",
    ),
    (
        (32, 314, 560, 46),
        "Release flow",
        "dev is free to build; test needs the manager's approval; prod needs the business approval. Only code moves.",
    ),
]

CSS = """
:root{--bg:#0d1117;--card:#111a33;--card2:#0b1020;--ink:#e6edf7;--muted:#93a1bd;--line:rgba(255,255,255,.08);
--cyan:#22d3ee;--violet:#8b5cf6;--green:#34d399;--gold:#f5b301;--rose:#f43f5e}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,'Segoe UI',Ubuntu,Arial,sans-serif}
a{color:#7cc4ff}main{max-width:920px;margin:0 auto;padding:24px 16px 60px}
h2{font-size:19px;margin:34px 0 12px;display:flex;gap:10px;align-items:center}
h2::after{content:"";flex:1;height:1px;background:var(--line)}
.card{background:linear-gradient(135deg,var(--card2),var(--card));border:1px solid var(--line);border-radius:18px;padding:22px}
.stage{position:relative;line-height:0}.stage img{width:100%;height:auto;border-radius:18px}
.spot{position:absolute;border-radius:10px;cursor:help;outline:none}
.spot:hover,.spot:focus-visible{background:rgba(255,255,255,.06);box-shadow:0 0 0 1px rgba(255,255,255,.18)}
.links{display:flex;gap:14px;justify-content:center;margin:14px 0 4px}.links img{width:64px;height:64px;display:block}
.links a{border-radius:50%;transition:transform .2s}.links a:hover{transform:translateY(-3px) scale(1.06)}
ul.about{margin:0;padding-left:20px}ul.about li{margin:4px 0}
table{border-collapse:collapse;width:100%;margin:14px 0}td{border:1px solid var(--line);padding:8px 12px;vertical-align:top}
.group{display:grid;grid-template-columns:150px 1fr;gap:10px;margin:10px 0;align-items:start}
.group .label{font-size:11.5px;font-weight:700;letter-spacing:.12em;color:var(--muted);padding-top:9px;text-transform:uppercase}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-flex;align-items:center;gap:8px;padding:6px 14px 6px 8px;border-radius:999px;text-decoration:none;color:var(--ink);
border:1.5px solid color-mix(in srgb,var(--c) 55%,transparent);background:color-mix(in srgb,var(--c) 10%,var(--card2));
font-size:13.5px;transition:transform .18s,box-shadow .18s;animation:rise .5s both;animation-delay:calc(var(--i)*35ms)}
.chip:hover,.chip:focus-visible{transform:translateY(-2px);box-shadow:0 6px 18px -6px var(--c);outline:none}
.chip img,.chip .mono{width:22px;height:22px;flex:none}
.mono{display:grid;place-items:center;border-radius:6px;font:800 10px/1 sans-serif;color:var(--c);background:color-mix(in srgb,var(--c) 22%,transparent)}
@keyframes rise{from{opacity:0;transform:translateY(8px)}}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.tile{border-radius:14px;padding:14px 16px;border:1px solid color-mix(in srgb,var(--c) 45%,transparent);
background:color-mix(in srgb,var(--c) 8%,transparent);cursor:help;animation:rise .6s both}
.tile b{display:block;font-size:30px;color:var(--c);line-height:1.2}.tile span{color:var(--muted);font-size:12.5px}
.row{display:grid;grid-template-columns:1fr;gap:22px;margin-top:22px}
.sub{font-weight:700;font-size:13px;margin:0 0 10px}
.matrix{display:grid;grid-auto-flow:column;grid-template-rows:repeat(7,11px);gap:3px;overflow-x:auto;padding-bottom:4px}
.matrix i{width:11px;height:11px;border-radius:2.5px;display:block;cursor:crosshair}
.matrix i:hover{outline:1.5px solid #fff}
.legend{display:flex;gap:4px;align-items:center;color:var(--muted);font-size:11.5px;margin-top:8px}.legend i{width:11px;height:11px;border-radius:2.5px}
.bar{display:flex;height:12px;border-radius:6px;overflow:hidden;margin-bottom:12px}.bar span{cursor:help;transition:filter .2s}.bar span:hover{filter:brightness(1.3)}
.langs{display:grid;grid-template-columns:repeat(4,1fr);gap:4px 14px;font-size:12.5px}.langs em{color:var(--muted);font-style:normal}
.dot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}
svg.graph{width:100%;height:auto;display:block;overflow:visible}
.trophies{display:grid;grid-template-columns:repeat(8,1fr);gap:10px}
.trophy{text-align:center;border-radius:14px;padding:12px 4px;border:1px solid color-mix(in srgb,var(--c) 40%,transparent);
background:color-mix(in srgb,var(--c) 6%,transparent);cursor:help;animation:rise .5s both;transition:transform .2s}
.trophy:hover{transform:translateY(-3px)}.trophy b{display:block;font-size:20px;color:var(--c)}.trophy small{display:block;color:var(--muted);font-size:11px}
.support{display:flex;flex-wrap:wrap;gap:12px;justify-content:center}.support img{display:block;width:270px;max-width:100%}
.support a{transition:transform .2s}.support a:hover{transform:translateY(-2px)}
#tip{position:fixed;z-index:9;max-width:300px;pointer-events:none;opacity:0;transform:translateY(4px);transition:opacity .15s,transform .15s;
background:#0b1020f2;border:1px solid rgba(255,255,255,.16);border-radius:12px;padding:10px 12px;font-size:13px;box-shadow:0 12px 30px -10px #000}
#tip.on{opacity:1;transform:none}#tip b{display:block;margin-bottom:2px}#tip span{color:var(--muted)}
#map{position:fixed;z-index:10;width:320px;height:230px;border-radius:14px;overflow:hidden;opacity:0;pointer-events:none;
transition:opacity .2s;border:1px solid rgba(255,255,255,.2);box-shadow:0 18px 40px -12px #000;background:#0b1020}
#map.on{opacity:1;pointer-events:auto}#map iframe{width:100%;height:100%;border:0}
#map a{position:absolute;right:8px;bottom:8px;background:#0b1020e6;padding:3px 8px;border-radius:8px;font-size:12px}
footer{margin-top:40px;color:var(--muted);font-size:12.5px;text-align:center}
@media (max-width:720px){.tiles{grid-template-columns:repeat(2,1fr)}.langs{grid-template-columns:1fr 1fr}
.trophies{grid-template-columns:repeat(4,1fr)}.group{grid-template-columns:1fr}.group .label{padding-top:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

JS = r"""
const D = JSON.parse(document.getElementById('data').textContent);
const tip = document.getElementById('tip'), map = document.getElementById('map');
let mapHide;
function place(el, x, y){const r = el.getBoundingClientRect(), vw = innerWidth, vh = innerHeight;
  let l = x + 14, t = y + 14; if (l + r.width > vw - 8) l = x - r.width - 14; if (t + r.height > vh - 8) t = y - r.height - 14;
  el.style.left = Math.max(8, l) + 'px'; el.style.top = Math.max(8, t) + 'px';}
function showTip(title, text, x, y){tip.replaceChildren();
  const b = document.createElement('b'); b.textContent = title; tip.append(b);
  if (text){const s = document.createElement('span'); s.textContent = text; tip.append(s);}
  tip.classList.add('on'); place(tip, x, y);}
function hideTip(){tip.classList.remove('on');}
function showMap(x, y){clearTimeout(mapHide);
  if (!map.querySelector('iframe')){const f = document.createElement('iframe'); f.src = map.dataset.src; f.loading = 'lazy';
    f.title = 'Map of Bengaluru'; f.referrerPolicy = 'no-referrer'; map.prepend(f);}
  map.classList.add('on'); place(map, x, y);}
function hideMapSoon(){mapHide = setTimeout(() => map.classList.remove('on'), 350);}
map.addEventListener('mouseenter', () => clearTimeout(mapHide)); map.addEventListener('mouseleave', hideMapSoon);
function bind(el, title, text){
  const on = e => { const p = e.touches ? e.touches[0] : e; const r = el.getBoundingClientRect();
    const x = p && p.clientX !== undefined ? p.clientX : r.right, y = p && p.clientY !== undefined ? p.clientY : r.bottom;
    title === 'map' ? showMap(x, y) : showTip(title, text, x, y); };
  el.addEventListener('mouseenter', on); el.addEventListener('mousemove', e => title === 'map' || place(tip, e.clientX, e.clientY));
  el.addEventListener('focus', on); el.addEventListener('touchstart', on, {passive: true});
  el.addEventListener('mouseleave', () => title === 'map' ? hideMapSoon() : hideTip()); el.addEventListener('blur', () => title === 'map' ? hideMapSoon() : hideTip());}
document.querySelectorAll('[data-tip-title]').forEach(el => bind(el, el.dataset.tipTitle, el.dataset.tipText || ''));
document.addEventListener('scroll', hideTip, {passive: true});

// matrix: the last 53 weeks, GitHub green, a tooltip per day
const days = D.days, dayMax = Math.max(1, ...days.map(d => d[1]));
const MATRIX = ['#1b2236', '#0e4429', '#006d32', '#26a641', '#39d353'];
const lvl = c => c === 0 ? 0 : Math.min(4, 1 + Math.floor(3.999 * c / dayMax));
const fmt = s => new Date(s + 'T00:00:00').toLocaleDateString('en-IN', {weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'});
const mx = document.getElementById('matrix');
const first = new Date(days[0][0] + 'T00:00:00').getDay();
for (let i = 0; i < first; i++) mx.append(Object.assign(document.createElement('i'), {style: 'visibility:hidden'}));
days.forEach(([d, c]) => { const i = document.createElement('i'); i.style.background = MATRIX[lvl(c)];
  i.tabIndex = -1; bind(i, `${c} contribution${c === 1 ? '' : 's'}`, fmt(d)); mx.append(i); });
document.getElementById('legend').append(...MATRIX.map(c => Object.assign(document.createElement('i'), {style: `background:${c}`})));

// graph: weekly totals with a crosshair and a tooltip per point
const weeks = []; for (let i = days.length % 7; i < days.length; i += 7) weeks.push({start: days[i][0], n: days.slice(i, i + 7).reduce((s, d) => s + d[1], 0)});
const G = document.getElementById('graph'), gw = 820, gh = 150, pad = 8, wmax = Math.max(1, ...weeks.map(w => w.n));
const px = i => pad + i * (gw - 2 * pad) / Math.max(1, weeks.length - 1), py = v => gh - pad - (gh - 2 * pad) * v / wmax;
const ns = 'http://www.w3.org/2000/svg', mk = (t, at) => { const e = document.createElementNS(ns, t); for (const k in at) e.setAttribute(k, at[k]); return e; };
const line = weeks.map((w, i) => `${i ? 'L' : 'M'}${px(i).toFixed(1)} ${py(w.n).toFixed(1)}`).join(' ');
G.append(mk('path', {d: `${line} L${px(weeks.length - 1)} ${gh} L${px(0)} ${gh} Z`, fill: 'url(#ga)'}),
  mk('path', {d: line, fill: 'none', stroke: 'url(#gl)', 'stroke-width': 2.4, 'stroke-linejoin': 'round', class: 'draw'}));
const cross = mk('line', {y1: 0, y2: gh, stroke: '#fff', 'stroke-opacity': .25, visibility: 'hidden'}), dot = mk('circle', {r: 5, fill: '#fde047', visibility: 'hidden'});
G.append(cross, dot);
const hit = mk('rect', {x: 0, y: 0, width: gw, height: gh, fill: 'transparent', style: 'cursor:crosshair'}); G.append(hit);
function onGraph(e){ const r = G.getBoundingClientRect(), x = (e.clientX - r.left) * gw / r.width;
  const i = Math.max(0, Math.min(weeks.length - 1, Math.round((x - pad) / ((gw - 2 * pad) / Math.max(1, weeks.length - 1)))));
  const w = weeks[i], prev = i ? weeks[i - 1].n : null;
  cross.setAttribute('x1', px(i)); cross.setAttribute('x2', px(i)); dot.setAttribute('cx', px(i)); dot.setAttribute('cy', py(w.n));
  cross.setAttribute('visibility', 'visible'); dot.setAttribute('visibility', 'visible');
  const delta = prev === null ? '' : ` · ${w.n - prev >= 0 ? '+' : ''}${w.n - prev} vs previous week`;
  showTip(`${w.n} contributions`, `Week of ${fmt(w.start)}${delta}`, e.clientX, e.clientY); }
hit.addEventListener('mousemove', onGraph); hit.addEventListener('touchmove', e => onGraph(e.touches[0]), {passive: true});
hit.addEventListener('mouseleave', () => { hideTip(); cross.setAttribute('visibility', 'hidden'); dot.setAttribute('visibility', 'hidden'); });
const months = document.getElementById('months'); let seen = -1;
weeks.forEach((w, i) => { const d = new Date(w.start + 'T00:00:00'); if (d.getMonth() !== seen && d.getDate() <= 7) { seen = d.getMonth();
  const t = mk('text', {x: px(i), y: gh + 16, fill: '#93a1bd', 'font-size': 11}); t.textContent = d.toLocaleDateString('en-IN', {month: 'short'}); months.append(t); } });
"""


def page(cfg, data):
    idt = cfg["identity"]
    total_bytes = sum(lang["bytes"] for lang in data["languages"]) or 1

    def spots(spec, w, h):
        out = []
        for (x, y, sw, sh), title, text in spec:
            style = (
                f"left:{100 * x / w:.2f}%;top:{100 * y / h:.2f}%;width:{100 * sw / w:.2f}%;height:{100 * sh / h:.2f}%"
            )
            out.append(
                f'<span class="spot" tabindex="0" style="{style}" data-tip-title="{a(title)}" data-tip-text="{a(text)}"></span>'
            )
        return "".join(out)

    links = []
    for b in cfg["buttons"]:
        url = cfg["dashboard"] if b["url"] == "dashboard" else idt["map_url"] if b["url"] == "map" else b["url"]
        title, _, text = b["tip"].partition(" · ")
        ext = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
        attrs = (
            'data-tip-title="map"'
            if b["key"] == "location"
            else f'data-tip-title="{a(title)}" data-tip-text="{a(text)}"'
        )
        links.append(f'<a href="{a(url)}"{ext} {attrs}><img src="assets/buttons/{b["key"]}.svg" alt="{a(title)}"></a>')

    groups, n = [], 0
    for g in cfg["skills"]:
        chips = []
        for it in g["items"]:
            logo = ROOT / "assets" / "logos" / f"{it['logo']}.svg"
            icon = (
                f'<img src="assets/logos/{it["logo"]}.svg" alt="">'
                if logo.exists()
                else f'<span class="mono">{a("".join(w[0] for w in it["name"].split()[:2]).upper())}</span>'
            )
            chips.append(
                f'<a class="chip" style="--c:{a(it["color"])};--i:{n}" href="{a(it["url"])}" target="_blank" rel="noopener" '
                f'data-tip-title="{a(it["name"])}" data-tip-text="{a(it["info"])}">{icon}{a(it["name"])}</a>'
            )
            n += 1
        groups.append(
            f'<div class="group"><div class="label">{a(g["group"])}</div><div class="chips">{"".join(chips)}</div></div>'
        )

    tiles = [
        (
            f"{data['total']:,}",
            "contributions, 12 months",
            "#22d3ee",
            "Contributions",
            "Commits, pull requests, issues and reviews in the last 12 months.",
        ),
        (
            data["current_streak"],
            "day streak now",
            "#34d399",
            "Current streak",
            "Days in a row with at least one contribution, up to today.",
        ),
        (
            data["longest_streak"],
            "longest streak",
            "#f5b301",
            "Longest streak",
            "The longest run of days with contributions in the last 12 months.",
        ),
        (
            data["repos"],
            "public repositories",
            "#8b5cf6",
            "Public repositories",
            "Own public repositories, forks not counted.",
        ),
    ]
    tile_html = "".join(
        f'<div class="tile" tabindex="0" style="--c:{c}" data-tip-title="{a(t)}" data-tip-text="{a(x)}"><b>{a(v)}</b><span>{a(lbl)}</span></div>'
        for v, lbl, c, t, x in tiles
    )
    bar = "".join(
        f'<span style="width:{100 * lang["bytes"] / total_bytes:.2f}%;background:{a(lang["color"])}" tabindex="0" '
        f'data-tip-title="{a(lang["name"])}" data-tip-text="{100 * lang["bytes"] / total_bytes:.1f}% of code in public repositories"></span>'
        for lang in data["languages"][:8]
    )
    legend = "".join(
        f'<div><span class="dot" style="background:{a(lang["color"])}"></span>{a(lang["name"])} '
        f"<em>{100 * lang['bytes'] / total_bytes:.1f}%</em></div>"
        for lang in data["languages"][:8]
    )
    rank_colors = {"SS": "#fde047", "S": "#f5b301", "A": "#c3cbd8", "B": "#cd7f32", "C": "#7c8aa5"}
    trophies = []
    for i, t in enumerate(data["trophies"]):
        names = ["C", "B", "A", "S", "SS"]
        nxt = next(((r, s) for r, s in zip(names, t["steps"], strict=True) if t["value"] < s), None)
        goal = f"Next rank {nxt[0]} at {nxt[1]}." if nxt else "Top rank reached."
        trophies.append(
            f'<div class="trophy" tabindex="0" style="--c:{rank_colors.get(t["rank"], "#3b4560")};animation-delay:{i * 60}ms" '
            f'data-tip-title="{a(t["label"])}: {a(t["value"])}" data-tip-text="Rank {a(t["rank"])}. {a(goal)}">'
            f"🏆<b>{a(t['rank'])}</b><small>{a(t['label'])}</small><small>{a(t['value'])}</small></div>"
        )
    support = "".join(
        f'<a href="{a(s["url"])}" target="_blank" rel="noopener" data-tip-title="{a(s["name"])}" data-tip-text="{a(s["sub"])}">'
        f'<img src="assets/support/{a(s["key"])}.svg" alt="{a(s["name"])}"></a>'
        for s in cfg["support"]
        if s["url"]
    )
    repos = "".join(
        f'<tr><td><a href="{a(r["url"])}" target="_blank" rel="noopener"><b>{a(r["name"])}</b></a></td><td>{a(r["about"])}</td></tr>'
        for r in cfg["project"]["repos"]
    )
    about = "".join(f"<li>{md_inline(x)}</li>" for x in cfg["about"])
    payload = json.dumps({"days": data["days"]}).replace("</", "<\\/")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{a(idt["name"])} · {a(idt["role"])}</title>
<meta name="description" content="{a(idt["name"])}, {a(idt["role"])} in {a(idt["place"])}: projects, skills and live GitHub activity.">
<style>{CSS}</style></head>
<body><main>
<div class="stage"><img src="assets/hero/hero.svg" alt="{a(idt["name"])}, {a(idt["role"])}, {a(idt["place"])}">{spots(HERO_SPOTS, 860, 300)}</div>
<nav class="links">{"".join(links)}</nav>

<h2>About me</h2><div class="card"><ul class="about">{about}</ul></div>

<h2>Featured project</h2>
<a class="stage" href="{a(cfg["project"]["url"])}" target="_blank" rel="noopener" style="display:block">
<img src="assets/project/lakehouse.svg" alt="{a(cfg["project"]["title"])}">{spots(PROJECT_SPOTS, 860, 432)}</a>
<table>{repos}</table><p>{a(cfg["project"]["note"])}</p>

<h2>Skills &amp; Tools</h2><div class="card">{"".join(groups)}</div>

<h2 id="activity">GitHub activity</h2>
<div class="card"><div class="tiles">{tile_html}</div>
<div class="row"><div><p class="sub">Matrix · last 12 months (hover a day)</p><div class="matrix" id="matrix"></div>
<div class="legend" id="legend">less&nbsp;</div></div>
<div><p class="sub">Languages in public repos</p><div class="bar">{bar}</div><div class="langs">{legend}</div>
<p style="color:var(--muted);font-size:12.5px;margin-top:14px">★ {a(data["stars"])} stars on public repositories</p></div></div>
<p class="sub" style="margin-top:22px">Graph · contributions per week (hover a point)</p>
<svg class="graph" id="graph" viewBox="0 0 820 170" role="img" aria-label="Contributions per week">
<defs><linearGradient id="gl" x1="0" y1="150" x2="0" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#5b21b6"/>
<stop offset=".33" stop-color="#c026d3"/><stop offset=".66" stop-color="#f97316"/><stop offset="1" stop-color="#fde047"/></linearGradient>
<linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f97316" stop-opacity=".4"/>
<stop offset="1" stop-color="#5b21b6" stop-opacity="0"/></linearGradient></defs><g id="months"></g></svg></div>

<h2 id="trophies">GitHub trophies</h2><div class="trophies">{"".join(trophies)}</div>

<h2 id="support-me">Support me</h2><div class="support">{support}</div>

<footer>Live data refreshed {a(data["updated"])} · built by GitHub Actions from
<a href="https://github.com/{a(cfg["owner"])}/{a(cfg["owner"])}">{a(cfg["owner"])}/{a(cfg["owner"])}</a> · no trackers.
The map is Google Maps and loads only when you hover or tap the location.</footer>
</main>
<div id="tip" role="tooltip"></div>
<div id="map" data-src="{a(idt["map_embed"])}"><a href="{a(idt["map_url"])}" target="_blank" rel="noopener">Open in Google Maps ↗</a></div>
<script type="application/json" id="data">{payload}</script>
<script>{JS}</script>
</body></html>
"""


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    cfg = yaml.safe_load((ROOT / "config" / "profile.yml").read_text(encoding="utf-8"))
    data = json.loads((out / "data.json").read_text(encoding="utf-8"))
    for sub in ("hero", "buttons", "project", "support", "logos"):  # the page uses the same artwork as the README
        shutil.copytree(ROOT / "assets" / sub, out / "assets" / sub, dirs_exist_ok=True)
    (out / "index.html").write_text(page(cfg, data), encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    print(f"{out / 'index.html'}: {len(data['days'])} days, {len(data['languages'])} languages")


if __name__ == "__main__":
    main()
