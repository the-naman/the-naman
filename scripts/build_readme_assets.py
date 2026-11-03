"""Builds every static SVG of the profile README from config/profile.yml (Python 3.11+, pyyaml).

    python scripts/build_readme_assets.py

Writes, one file per clickable item so each can carry its own link and tooltip in README.md:
    assets/hero/hero.svg            header: name, role, location, typing lines, quotes, Bronze/Silver/Gold
    assets/hero/divider.svg         animated wave between sections
    assets/buttons/<key>.svg        round icon links under the header
    assets/project/lakehouse.svg    featured project diagram
    assets/skills/<slug>.svg        one chip per skill (logo + name)
    assets/support/<key>.svg        support cards
Live cards (activity, trophies, snake) are built by the workflow: scripts/build_github_stats.py.
"""

import re
import sys

import yaml

from svg_kit import (
    ASSETS,
    BG0,
    BG1,
    BRONZE,
    CYAN,
    FONT,
    GOLD,
    GREEN,
    INK,
    MONO,
    MUTED,
    NAME_PATH,
    NAME_W,
    ORANGE,
    ROOT,
    ROSE,
    SILVER,
    VIOLET,
    W,
    appear,
    aurora,
    aurora_defs,
    blob,
    card,
    divider,
    dots,
    engineer_icon,
    escape,
    flow_path,
    heart,
    logo,
    medallion,
    node,
    packet,
    pin,
    typing,
    write,
)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def hero(idt):
    h = 300
    defs = aurora_defs() + (
        f'<linearGradient id="nameg2" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox" spreadMethod="repeat">'
        '<stop offset="0" stop-color="#67e8f9"/><stop offset=".35" stop-color="#a5b4fc"/><stop offset=".65" stop-color="#f0abfc"/>'
        '<stop offset="1" stop-color="#67e8f9"/>'
        '<animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0" dur="8s" repeatCount="indefinite"/>'
        "</linearGradient>"
        '<filter id="nglow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="9"/></filter>'
        f'<clipPath id="nclip"><path d="{NAME_PATH}"/></clipPath>'
        '<linearGradient id="nshine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    )
    body = (
        aurora(W, h)
        + f'<text x="48" y="78" font-family="{FONT}" font-size="18" fill="{MUTED}">Hi there, I’m</text>'
        + f'<g transform="translate(46 146)" aria-label="{escape(idt["name"])}">'
        f'<path d="{NAME_PATH}" fill="#8b5cf6" opacity=".55" filter="url(#nglow)">'
        f'<animate attributeName="opacity" values=".35;.65;.35" dur="5s" repeatCount="indefinite"/></path>'
        f'<path d="{NAME_PATH}" fill="url(#nameg2)"/>'
        f'<g clip-path="url(#nclip)"><rect x="-120" y="-70" width="70" height="90" fill="url(#nshine)" '
        f'transform="skewX(-20)"><animate attributeName="x" values="-120;{NAME_W + 120}" dur="4.5s" begin="1s" '
        f'repeatCount="indefinite"/></rect></g></g>'
        + engineer_icon(48, 169, CYAN)
        + f'<text x="74" y="186" font-family="{FONT}" font-size="20" fill="{INK}" textLength="128" '
        f'lengthAdjust="spacingAndGlyphs">{escape(idt["role"])}</text>'
        + pin(214, 168, ROSE)
        + f'<text x="234" y="186" font-family="{FONT}" font-size="20" fill="{INK}">{escape(idt["place"])}</text>'
        + typing(idt["quotes"], 48, 34, 12, "#c4b5fd", slot=7.0, pid="tq", opacity=0.55)
        + typing(idt["typing"], 48, 228, 17, CYAN)
        + f'<g transform="translate(48 252)"><rect width="{len(idt["status"]) * 7.6 + 44}" height="30" rx="15" '
        f'fill="{GREEN}" fill-opacity=".12" stroke="{GREEN}" stroke-opacity=".5"/>'
        f'<circle cx="16" cy="15" r="5" fill="{GREEN}"><animate attributeName="r" values="4;6;4" dur="1.6s" repeatCount="indefinite"/></circle>'
        f'<circle cx="16" cy="15" r="5" fill="none" stroke="{GREEN}"><animate attributeName="r" values="5;13" dur="1.6s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values=".8;0" dur="1.6s" repeatCount="indefinite"/></circle>'
        f'<text x="30" y="20" font-family="{FONT}" font-size="13.5" font-weight="600" fill="{GREEN}">{escape(idt["status"])}</text></g>'
        + medallion(705, 150)
    )
    return card(h, body, defs)


def lakehouse(title):
    h = 432
    body = [f'<rect width="{W}" height="{h}" fill="url(#dots)"/>', blob(760, 60, 110, ORANGE, -40, 30, 18, 0.18)]
    body.append(
        f'<text x="32" y="44" font-family="{FONT}" font-weight="800" font-size="22" fill="{INK}">{escape(title)}</text>'
        f'<text x="32" y="68" font-family="{FONT}" font-size="13.5" fill="{MUTED}">A healthcare group acquires a lender: '
        f"two companies, three environments, one trusted group view every night</text>"
    )
    # nodes: sources, bronze, silver, gold, outputs
    y0 = 100
    body.append(node(28, y0, 150, 74, "Sources", "S3: CSV, JSON, Excel|PDF + OCR of images", CYAN, 0.0))
    body.append(node(28, y0 + 100, 150, 74, "Kafka", "payment events|Structured Streaming", VIOLET, 0.2))
    body.append(node(222, y0 + 40, 130, 94, "Bronze", "Auto Loader|raw, nothing lost", BRONZE, 0.4))
    body.append(node(392, y0 + 40, 130, 94, "Silver", "SCD2, quarantine|quality checkpoint", SILVER, 0.6))
    body.append(node(562, y0 + 40, 120, 94, "Gold", "SQL star schema|reconciled", GOLD, 0.8))
    body.append(node(718, y0, 116, 74, "Group view", "people matched|across companies", GREEN, 1.0))
    body.append(node(718, y0 + 100, 116, 74, "BI + alerts", "masked dashboards|HTML alert mails", ORANGE, 1.2))
    paths = {
        "p1": f"M178 {y0 + 37} C200 {y0 + 37} 200 {y0 + 87} 222 {y0 + 87}",
        "p2": f"M178 {y0 + 137} C200 {y0 + 137} 200 {y0 + 87} 222 {y0 + 87}",
        "p3": f"M352 {y0 + 87} L392 {y0 + 87}",
        "p4": f"M522 {y0 + 87} L562 {y0 + 87}",
        "p5": f"M682 {y0 + 87} C700 {y0 + 87} 700 {y0 + 37} 718 {y0 + 37}",
        "p6": f"M682 {y0 + 87} C700 {y0 + 87} 700 {y0 + 137} 718 {y0 + 137}",
    }
    for pid, d in paths.items():
        body.append(flow_path(pid, d))
    colors = [CYAN, VIOLET, BRONZE, SILVER, GREEN, ORANGE]
    for k, pid in enumerate(paths):
        for j in range(2):
            body.append(packet(pid, colors[k], 1.6, 1.4 + j * 0.8 + k * 0.15))
    # environments lane
    ly = 300
    body.append(
        f'<text x="32" y="{ly}" font-family="{FONT}" font-weight="700" font-size="13" fill="{INK}">'
        f"Only code moves between environments, never data</text>"
    )
    envs = [("dev", MUTED, "free to build"), ("test", CYAN, "manager approves"), ("prod", GREEN, "business approves")]
    for i, (env, col, sub) in enumerate(envs):
        x = 32 + i * 200
        body.append(
            f'<g><rect x="{x}" y="{ly + 14}" width="150" height="46" rx="10" fill="{col}" fill-opacity=".1" stroke="{col}" '
            f'stroke-opacity=".6"/><text x="{x + 16}" y="{ly + 34}" font-family="{MONO}" font-weight="700" font-size="14" '
            f'fill="{col}">{env}</text><text x="{x + 16}" y="{ly + 51}" font-family="{FONT}" font-size="11" fill="{MUTED}">'
            f"{sub}</text></g>"
        )
        if i < 2:
            ax = x + 150
            body.append(
                f'<path id="e{i}" d="M{ax + 4} {ly + 37} L{ax + 46} {ly + 37}" stroke="#ffffff" stroke-opacity=".25" '
                f'stroke-width="2"/>{packet(f"e{i}", col if i else CYAN, 1.4, i * 0.7)}'
                f'<text x="{ax + 25}" y="{ly + 30}" text-anchor="middle" font-size="12" fill="{GOLD}">✓</text>'
            )
    chips = ["PR approvals", "10 CI checks + tests", "column masks", "service principals", "hotfix + back-merge"]
    cx = 640
    # right column: safeguards list
    for i, c in enumerate(chips):
        yy = ly - 2 + i * 21
        body.append(
            f"<g>{appear(1.6 + i * 0.25)}"
            f'<circle cx="{cx}" cy="{yy - 4}" r="3.5" fill="{GREEN}"/><text x="{cx + 12}" y="{yy}" font-family="{FONT}" '
            f'font-size="12.5" fill="{INK}">{escape(c)}</text></g>'
        )
    body.append(
        f'<text x="32" y="{h - 22}" font-family="{FONT}" font-size="12" fill="{MUTED}">Databricks · PySpark · '
        f"SQL · Unity Catalog · Kafka · AWS S3 · GitHub Actions · Asset Bundles · all data synthetic</text>"
    )
    return card(h, "".join(body), dots(W, h))


def icon_button(icon, color, beat=False):
    """Round, icon-only link button with a pulsing ring (assets/buttons/<key>.svg)."""
    w = h = 64
    pulse = (
        '<animateTransform attributeName="transform" type="scale" additive="sum" values="1;1.12;1;1.08;1" '
        'keyTimes="0;.15;.3;.45;1" dur="1.6s" repeatCount="indefinite"/>'
        if beat
        else ""
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient></defs>
<circle cx="32" cy="32" r="26" fill="url(#b)" stroke="{color}" stroke-opacity=".7" stroke-width="1.5"/>
<circle cx="32" cy="32" r="26" fill="none" stroke="{color}">
<animate attributeName="r" values="26;31;26" dur="2.6s" repeatCount="indefinite"/>
<animate attributeName="stroke-opacity" values=".55;0;.55" dur="2.6s" repeatCount="indefinite"/></circle>
<g transform="translate(32 32)"><g>{pulse}<g transform="translate(-14 -14)">{icon}</g></g></g>
</svg>
"""


def location_icon(color):
    return f'<g transform="translate(7 2) scale(1.0)">{pin(0, 0, color)}</g>'


def chart_icon(color):
    return (
        f'<g fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M3 3v22h22"/><path d="M7 19l5-6 4 3 7-9"><animate attributeName="stroke-dasharray" '
        f'values="0 40;40 0" dur="2.4s" repeatCount="indefinite"/></path></g>'
    )


def employer_badge(key):
    """Small white badge with an employer's logo (assets/badges/<key>.svg), readable on GitHub's light and dark themes."""
    w, h = 96, 26
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="7" fill="#ffffff" stroke="#d0d7de"/>
<g>{appear(0.2, 0.5)}<svg x="8" y="2" width="{w - 16}" height="{h - 4}" viewBox="0 -19.94 159.45 69.59">{(ASSETS / "logos" / f"{key}.svg").read_text(encoding="utf-8").split(">", 1)[1].rsplit("</svg>", 1)[0]}</svg></g>
</svg>
"""


GROUP_COLORS = ["#22d3ee", "#a78bfa", "#38bdf8", "#f59e0b", "#facc15", "#34d399", "#60a5fa", "#f472b6"]


def group_label(name, count, color):
    """Section label above a skill group (assets/skills/group-<slug>.svg): bold title, item count, an accent line
    that draws itself, so every chip below clearly belongs to it."""
    w, h = 820, 40
    tw = round(len(name) * 11.2 + 28)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<title>{escape(name)}</title>
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{color}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/></linearGradient></defs>
<rect x="0" y="9" width="5" height="22" rx="2.5" fill="{color}"/>
<text x="16" y="27" font-family="{FONT}" font-weight="800" font-size="18" letter-spacing=".6" fill="{color}">{escape(name)}</text>
<text x="{tw}" y="27" font-family="{FONT}" font-size="12.5" fill="{MUTED}">{count} {"tool" if count == 1 else "tools"}</text>
<rect x="{tw + 62}" y="19" height="2" rx="1" width="{w - tw - 62}" fill="url(#l)">
<animate attributeName="width" values="0;0;{w - tw - 62}" keyTimes="0;.2;1" dur="1.6s" fill="freeze"/></rect>
</svg>
"""


def skill_chip(item, index):
    """One skill (assets/skills/<slug>.svg): dark pill with the logo and the official name; fades in, then a light
    sweep passes over it now and then. Its own dark background keeps it readable on GitHub's light and dark themes."""
    name, color = item["name"], item["color"]
    w, h = round(len(name) * 7.3 + 50), 36
    d = 0.1 + (index % 12) * 0.06
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<title>{escape(name)}</title>
<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".12"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect width="{w}" height="{h}" rx="18"/></clipPath></defs>
<g>{appear(d, 0.45, 6)}
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#b)"/><rect width="{w}" height="{h}" fill="{color}" fill-opacity=".1"/>
<rect x="-60" width="40" height="{h}" fill="url(#sw)" transform="skewX(-20)"><animate attributeName="x" values="-60;-60;{w + 60}" keyTimes="0;.7;1" dur="{7 + index % 5}s" begin="{d + 1:.2f}s" repeatCount="indefinite"/></rect></g>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="17.25" fill="none" stroke="{color}" stroke-opacity=".55" stroke-width="1.5"/>
{logo(item["logo"], 9, 7, 22, color, name)}
<text x="38" y="23" font-family="{FONT}" font-size="13.5" fill="{INK}">{escape(name)}</text></g>
</svg>
"""


def support_card(key, label, sub, color):
    """Wide support link (assets/support/<key>.svg): the owner's logo file, or a monogram until one is added."""
    w, h = 270, 64
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".08"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect width="{w}" height="{h}" rx="16"/></clipPath></defs>
<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="url(#b)"/>
<rect x="-120" width="80" height="{h}" fill="url(#sw)" transform="skewX(-20)"><animate attributeName="x" values="-120;{w + 120}" dur="5s" repeatCount="indefinite"/></rect></g>
<rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="16" fill="none" stroke="{color}" stroke-opacity=".6" stroke-width="1.5"/>
{logo(key, 16, 14, 36, color, label)}
<text x="66" y="29" font-family="{FONT}" font-weight="700" font-size="15" fill="{INK}">{escape(label)}</text>
<text x="66" y="47" font-family="{FONT}" font-size="12" fill="{MUTED}">{escape(sub)}</text>
<text x="{w - 18}" y="38" text-anchor="end" font-family="{FONT}" font-size="17" fill="{color}">\u2192
<animate attributeName="x" values="{w - 20};{w - 14};{w - 20}" dur="1.8s" repeatCount="indefinite"/></text>
</svg>
"""


def main():
    cfg = yaml.safe_load((ROOT / "config" / "profile.yml").read_text(encoding="utf-8"))
    idt = cfg["identity"]
    write(ASSETS / "hero" / "hero.svg", hero(idt))
    write(ASSETS / "hero" / "divider.svg", divider())
    write(ASSETS / "project" / "lakehouse.svg", lakehouse(cfg["project"]["title"]))
    icons = {
        "linkedin": (logo("linkedin", 0, 0, 28, "#0a66c2", "in"), "#0a66c2", False),
        "portfolio": (logo("known", 0, 0, 28, CYAN, "Portfolio"), CYAN, False),
        "location": (location_icon(ROSE), ROSE, False),
        "dashboard": (chart_icon(GREEN), GREEN, False),
        "support": (heart(ROSE), ROSE, True),
    }
    for b in cfg["buttons"]:
        icon, color, beat = icons[b["key"]]
        write(ASSETS / "buttons" / f"{b['key']}.svg", icon_button(icon, color, beat))
    n = 0
    for gi, group in enumerate(cfg["skills"]):
        color = GROUP_COLORS[gi % len(GROUP_COLORS)]
        write(
            ASSETS / "skills" / f"group-{slug(group['group'])}.svg",
            group_label(group["group"], len(group["items"]), color),
        )
        for item in group["items"]:
            write(ASSETS / "skills" / f"{slug(item['name'])}.svg", skill_chip(item, n))
            n += 1
    for key, e in (cfg.get("employers") or {}).items():
        write(ASSETS / "badges" / f"{key}.svg", employer_badge(e["logo"]))
    for s in cfg["support"]:
        if not s["url"]:  # no link yet: no card
            continue
        write(ASSETS / "support" / f"{s['key']}.svg", support_card(s["key"], s["name"], s["sub"], s["color"]))


if __name__ == "__main__":
    sys.exit(main())
