"""Live GitHub data for the profile: dist/stats.svg, dist/trophies.svg and dist/data.json (used by the dashboard).
Standard library only.

Run every 3 hours by .github/workflows/profile.yml with the workflow's own GITHUB_TOKEN (read-only, public data):
one GraphQL call. No third-party stats or trophy service. A new language in any public repo appears by itself.

    python scripts/build_github_stats.py the-naman dist            # live (needs GITHUB_TOKEN)
    python scripts/build_github_stats.py the-naman dist --sample   # made-up numbers, for a design preview only
"""

import json
import os
import random
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svg_kit import (  # noqa: E402
    CYAN,
    FONT,
    GOLD,
    GREEN,
    INK,
    MUTED,
    VIOLET,
    W,
    appear,
    aurora_defs,
    card,
    dots,
)

IST = timezone(timedelta(hours=5, minutes=30))
# heat scale (cold -> hot), clear steps on the dark card: empty, violet, magenta, orange, yellow
HEAT = ["#1e2340", "#5b21b6", "#c026d3", "#f97316", "#fde047"]  # graph line and area
# matrix: GitHub's own green scale (dark theme), so the grid reads like the contribution graph people know
MATRIX = ["#1b2236", "#0e4429", "#006d32", "#26a641", "#39d353"]

QUERY = """query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions totalPullRequestContributions totalIssueContributions
      totalPullRequestReviewContributions restrictedContributionsCount
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes { stargazerCount languages(first: 20, orderBy: {field: SIZE, direction: DESC}) {
        edges { size node { name color } } } }
    }
  }
}"""


def fetch(login):
    req = urllib.request.Request(  # noqa: S310 - fixed https://api.github.com URL
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 - fixed https://api.github.com URL
        data = json.load(r)
    if data.get("errors"):
        sys.exit(f"GitHub API: {data['errors'][0].get('message')}")
    u = data["data"]["user"]
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            size, color = langs.get(n, (0, e["node"]["color"]))
            langs[n] = (size + e["size"], e["node"]["color"] or color or MUTED)
    created = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00")).date()
    return {
        "total": cal["totalContributions"],
        "days": [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]],
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "langs": langs,
        "commits": cc["totalCommitContributions"] + cc["restrictedContributionsCount"],
        "prs": cc["totalPullRequestContributions"],
        "reviews": cc["totalPullRequestReviewContributions"],
        "followers": u["followers"]["totalCount"],
        "years": (date.today() - created).days / 365.25,
    }


def sample():
    rnd = random.Random(7)  # noqa: S311 - preview numbers only
    start = date.today() - timedelta(363)
    days = []
    for d in range(364):
        burst = 1 + (d // 30) % 3
        days.append(((start + timedelta(d)).isoformat(), rnd.choice([0, 0, 1, 2, 3, 5, 8, 12]) * burst // 2))
    langs = {
        "Python": (620, "#3572A5"),
        "Jupyter Notebook": (210, "#DA5B0B"),
        "SQL": (160, "#e38c00"),
        "HTML": (120, "#e34c26"),
        "JavaScript": (90, "#f1e05a"),
        "Shell": (30, "#89e051"),
        "CSS": (25, "#663399"),
    }
    return {
        "total": sum(c for _, c in days),
        "days": days,
        "repos": 14,
        "stars": 6,
        "langs": langs,
        "commits": 980,
        "prs": 52,
        "reviews": 18,
        "followers": 9,
        "years": 3.4,
    }


def streaks(days):
    """(current, longest) streak of days with at least one contribution; today may still be empty."""
    longest = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur, items = 0, list(days)
    if items and items[-1][1] == 0:
        items = items[:-1]
    for _, c in reversed(items):
        if not c:
            break
        cur += 1
    return cur, longest


ICONS = {  # small original line icons, drawn in a 24 x 24 box
    "commit": '<circle cx="12" cy="12" r="4.5"/><path d="M1 12h6.5M16.5 12H23"/>',
    "flame": '<path d="M12 2c1 4 6 6.5 6 12a6 6 0 0 1-12 0c0-3 1.5-4.5 3-6 0 2 1 3 2 3 0-3-1-6 1-9z"/>',
    "trophy": '<path d="M7 3h10v5a5 5 0 0 1-10 0z"/><path d="M7 5H3.5a3.5 3.5 0 0 0 3.5 4M17 5h3.5a3.5 3.5 0 0 1-3.5 4"/>'
    '<path d="M12 13v4M8 21h8M9 17h6v4H9z"/>',
    "repo": '<path d="M5 3h12a2 2 0 0 1 2 2v16H7a2 2 0 0 1-2-2z"/><path d="M5 19a2 2 0 0 1 2-2h12M9 7h6"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "star": '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9z"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/>'
    '<rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    "chart": '<path d="M3 3v18h18"/><path d="M6 15l4-5 4 3 6-7"/>',
    "pr": '<circle cx="6" cy="5" r="2.5"/><circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="19" r="2.5"/>'
    '<path d="M6 7.5v9M18 16.5V9a3 3 0 0 0-3-3h-4M13 3.5 10.5 6 13 8.5"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.8"/>'
    '<path d="M16 14.2a5.2 5.2 0 0 1 5.5 5.3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
}


def icon(name, x, y, color, size=22, anim=""):
    return (
        f'<g transform="translate({x} {y}) scale({size / 24:.3f})" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}{anim}</g>'
    )


def heat(c, top):
    return MATRIX[0] if c == 0 else MATRIX[min(4, 1 + int(3.999 * c / max(top, 1)))]


def tile(x, y, value, label, color, delay, ico):
    if ico == "flame":  # the flame flickers, the others breathe
        anim = (
            '<animateTransform attributeName="transform" type="scale" additive="sum" '
            'values="1 1;1.06 .94;.96 1.05;1 1" dur="1.1s" repeatCount="indefinite"/>'
        )
    else:
        anim = '<animate attributeName="opacity" values="1;.55;1" dur="3s" repeatCount="indefinite"/>'
    return (
        f"<g>{appear(delay, 0.6, 10)}"
        f'<rect x="{x}" y="{y}" width="186" height="86" rx="14" fill="{color}" fill-opacity=".08" stroke="{color}" '
        f'stroke-opacity=".45"/>{icon(ico, x + 146, y + 14, color, 24, anim)}'
        f'<text x="{x + 18}" y="{y + 48}" font-family="{FONT}" font-weight="800" font-size="32" fill="{color}">'
        f'{escape(str(value))}</text><text x="{x + 18}" y="{y + 70}" font-family="{FONT}" font-size="12.5" '
        f'fill="{MUTED}">{escape(label)}</text></g>'
    )


def heat_legend(x, y):
    out = f'<text x="{x}" y="{y + 9}" font-family="{FONT}" font-size="11.5" fill="{MUTED}">less</text>'
    for i, c in enumerate(MATRIX):
        out += f'<rect x="{x + 30 + i * 15}" y="{y}" width="11" height="11" rx="2.5" fill="{c}"/>'
    return out + f'<text x="{x + 110}" y="{y + 9}" font-family="{FONT}" font-size="11.5" fill="{MUTED}">more</text>'


def graph(days, x0, y0, w, h):
    """Weekly contributions of the last 52 weeks: area + line coloured by heat (hotter = higher), drawn in."""
    weeks = [sum(c for _, c in days[i : i + 7]) for i in range(max(0, len(days) - 364), len(days), 7)][-52:]
    top = max(weeks + [1])
    n = len(weeks)
    pts = [(x0 + i * w / max(n - 1, 1), y0 + h - h * v / top) for i, v in enumerate(weeks)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = f"{line} L{pts[-1][0]:.1f} {y0 + h} L{x0} {y0 + h} Z"
    out = [
        f'<linearGradient id="hv" x1="0" y1="{y0 + h}" x2="0" y2="{y0}" gradientUnits="userSpaceOnUse">'
        + "".join(f'<stop offset="{k / 4}" stop-color="{c}"/>' for k, c in enumerate(HEAT[1:] + [HEAT[4]]))
        + "</linearGradient>",
        f'<linearGradient id="ha" x1="0" y1="{y0}" x2="0" y2="{y0 + h}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="{HEAT[3]}" stop-opacity=".45"/><stop offset="1" stop-color="{HEAT[1]}" stop-opacity="0"/>'
        "</linearGradient>",
    ]
    for k in range(4):  # faint grid
        yy = y0 + k * h / 3
        out.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x0 + w}" y2="{yy:.1f}" stroke="#fff" stroke-opacity=".05"/>')
    out.append(f'<path d="{area}" fill="url(#ha)">{appear(1.6, 1.2)}</path>')
    out.append(
        f'<path d="{line}" fill="none" stroke="url(#hv)" stroke-width="2.4" stroke-linejoin="round" pathLength="1" '
        f'stroke-dasharray="1" stroke-dashoffset="0"><animate attributeName="stroke-dashoffset" values="1;1;0" '
        f'keyTimes="0;.4;1" dur="3.4s" fill="freeze"/></path>'
    )
    peak = max(range(n), key=lambda i: weeks[i])
    px, py = pts[peak]
    out.append(
        f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{HEAT[4]}">{appear(3.2, 0.3)}'
        f'<animate attributeName="r" values="3.5;6;3.5" dur="1.8s" repeatCount="indefinite"/></circle>'
        f'<text x="{px:.1f}" y="{py - 10:.1f}" text-anchor="middle" font-family="{FONT}" font-size="11" '
        f'fill="{HEAT[4]}">peak {weeks[peak]}/wk{appear(3.2, 0.3)}</text>'
    )
    # month labels
    start = date.fromisoformat(days[-n * 7][0]) if len(days) >= n * 7 else date.today()
    seen = set()
    for i in range(n):
        d = start + timedelta(7 * i)
        if d.month not in seen and d.day <= 7:
            seen.add(d.month)
            out.append(
                f'<text x="{x0 + i * w / max(n - 1, 1):.1f}" y="{y0 + h + 16}" font-family="{FONT}" '
                f'font-size="10.5" fill="{MUTED}">{d.strftime("%b")}</text>'
            )
    return "".join(out)


def render_stats(d, updated):
    days = d["days"]
    cur, best = streaks(days)
    h = 560
    body = [
        f'<rect width="{W}" height="{h}" fill="url(#dots)"/>',
        icon("code", 32, 22, CYAN, 22),
        f'<text x="62" y="40" font-family="{FONT}" font-weight="800" font-size="20" fill="{INK}">GitHub activity</text>',
        f'<circle cx="{W - 40 - len(updated) * 6.3 - 92:.0f}" cy="36" r="4" fill="{GREEN}"><animate '
        f'attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>',
        f'<text x="{W - 32}" y="40" text-anchor="end" font-family="{FONT}" font-size="12" fill="{MUTED}">'
        f"live · refreshed {escape(updated)}</text>",
    ]
    tiles = [
        (f"{d['total']:,}", "contributions, 12 months", CYAN, "commit"),
        (cur, "day streak now", GREEN, "flame"),
        (best, "longest streak", GOLD, "trophy"),
        (d["repos"], "public repositories", VIOLET, "repo"),
    ]
    for i, (v, label, col, ico) in enumerate(tiles):
        body.append(tile(32 + i * 202, 62, v, label, col, 0.1 + i * 0.15, ico))
    # matrix view: last 26 weeks, heat colours, revealed column by column, newest week pulsing
    recent = days[-26 * 7 :]
    top = max([c for _, c in recent] + [1])
    hx, hy = 32, 194
    body.append(icon("grid", hx, hy - 24, MUTED, 15))
    body.append(
        f'<text x="{hx + 22}" y="{hy - 11}" font-family="{FONT}" font-weight="700" font-size="13" '
        f'fill="{INK}">Matrix · last 26 weeks</text>'
    )
    for k, (_, c) in enumerate(recent):
        col, row = divmod(k, 7)
        pulse = (
            '<animate attributeName="fill-opacity" values="1;.45;1" dur="2s" repeatCount="indefinite"/>'
            if k >= len(recent) - 7 and c
            else ""
        )
        body.append(
            f'<rect x="{hx + col * 16}" y="{hy + row * 16}" width="12" height="12" rx="3" fill="{heat(c, top)}">'
            f"{appear(0.6 + col * 0.04, 0.3)}{pulse}</rect>"
        )
    body.append(heat_legend(hx, hy + 7 * 16 + 8))
    # languages
    lx, ly, lw = 476, 194, 352
    body.append(icon("code", lx, ly - 24, MUTED, 15))
    body.append(
        f'<text x="{lx + 22}" y="{ly - 11}" font-family="{FONT}" font-weight="700" font-size="13" '
        f'fill="{INK}">Languages in public repos</text>'
    )
    langs = d["langs"]
    tot = sum(sz for sz, _ in langs.values()) or 1
    shown = sorted(langs.items(), key=lambda kv: -kv[1][0])[:8]
    body.append(
        f'<clipPath id="bar"><rect x="{lx}" y="{ly}" width="{lw}" height="12" rx="6"/></clipPath>'
        f'<g clip-path="url(#bar)">'
    )
    x = lx
    for i, (_name, (size, color)) in enumerate(shown):
        wseg = max(3, round(lw * size / tot))
        t = 1.4 + i * 0.12
        body.append(
            f'<rect x="{x}" y="{ly}" height="12" width="{wseg}" fill="{color}"><animate attributeName="width" '
            f'values="0;0;{wseg}" keyTimes="0;{(t - 0.6) / t:.3f};1" dur="{t:.2f}s" fill="freeze"/></rect>'
        )
        x += wseg
    body.append(
        f'<rect x="{lx - 80}" y="{ly}" width="60" height="12" fill="url(#sweep2)"><animate attributeName="x" '
        f'values="{lx - 80};{lx + lw + 20}" dur="4s" begin="2s" repeatCount="indefinite"/></rect></g>'
    )
    for i, (name, (size, color)) in enumerate(shown):
        r, c = divmod(i, 2)
        tx, ty = lx + c * 180, ly + 36 + r * 23
        body.append(
            f"<g>{appear(1.2 + i * 0.1, 0.4)}"
            f'<circle cx="{tx + 5}" cy="{ty - 4}" r="5" fill="{color}"/><text x="{tx + 16}" y="{ty}" '
            f'font-family="{FONT}" font-size="12.5" fill="{INK}">{escape(name)} '
            f'<tspan fill="{MUTED}">{100 * size / tot:.1f}%</tspan></text></g>'
        )
    # graph view: weekly totals, 12 months
    gy = 370
    body.append(icon("chart", 32, gy - 24, MUTED, 15))
    body.append(
        f'<text x="54" y="{gy - 11}" font-family="{FONT}" font-weight="700" font-size="13" fill="{INK}">'
        f"Graph · contributions per week, 12 months</text>"
    )
    body.append(graph(days, 40, gy + 14, W - 80, 120))
    body.append(
        icon(
            "star",
            W - 210,
            h - 30,
            GOLD,
            14,
            '<animateTransform attributeName="transform" type="rotate" additive="sum" '
            'values="0 12 12;360 12 12" dur="8s" repeatCount="indefinite"/>',
        )
    )
    body.append(
        f'<text x="{W - 190}" y="{h - 19}" font-family="{FONT}" font-size="12" fill="{MUTED}">'
        f"{d['stars']} stars on public repositories</text>"
    )
    sweep2 = (
        '<linearGradient id="sweep2" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".45"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
        "</linearGradient>"
    )
    return card(h, "".join(body), dots(W, h) + aurora_defs() + sweep2)


RANKS = [("SS", "#fde047"), ("S", GOLD), ("A", "#c3cbd8"), ("B", "#cd7f32"), ("C", "#7c8aa5")]


def rank(value, steps):
    """steps = thresholds for C, B, A, S, SS. Returns (rank, colour) or ('-', dim) below C."""
    for i in range(4, -1, -1):
        if value >= steps[i]:
            return RANKS[4 - i]
    return "–", "#3b4560"


def trophy_items(d):
    """(label, value, thresholds C..SS, icon) for every trophy."""
    _cur, best = streaks(d["days"])
    return [
        ("Contributions", d["total"], (100, 300, 700, 1500, 3000), "commit"),
        ("Commits", d["commits"], (50, 200, 500, 1000, 2000), "commit"),
        ("Streak", best, (7, 14, 30, 60, 100), "flame"),
        ("Repositories", d["repos"], (3, 10, 20, 35, 50), "repo"),
        ("Languages", len(d["langs"]), (3, 5, 8, 12, 16), "code"),
        ("Pull requests", d["prs"], (1, 10, 30, 100, 300), "pr"),
        ("Stars", d["stars"], (1, 10, 30, 100, 300), "star"),
        ("Years on GitHub", round(d["years"], 1), (1, 2, 4, 6, 8), "clock"),
    ]


def render_trophies(d):
    items = trophy_items(d)
    h = 196
    cw = (W - 64) / len(items)
    body = [
        f'<rect width="{W}" height="{h}" fill="url(#dots)"/>',
        icon("trophy", 32, 20, GOLD, 22),
        f'<text x="62" y="38" font-family="{FONT}" font-weight="800" font-size="20" fill="{INK}">GitHub trophies</text>',
        f'<text x="{W - 32}" y="38" text-anchor="end" font-family="{FONT}" font-size="12" fill="{MUTED}">'
        f"ranks C → B → A → S → SS, live</text>",
    ]
    for i, (label, value, steps, ico) in enumerate(items):
        r, col = rank(value, steps)
        x = 32 + i * cw
        cx = x + cw / 2
        dly = 0.15 + i * 0.12
        float_anim = (
            f'<animateTransform attributeName="transform" type="translate" additive="sum" values="0 0;0 -3;0 0" '
            f'dur="{3 + (i % 3) * 0.4:.1f}s" begin="{i * 0.3:.1f}s" repeatCount="indefinite"/>'
        )
        glow = (
            f'<circle cx="{cx:.1f}" cy="96" r="30" fill="{col}" opacity=".12"><animate attributeName="opacity" '
            f'values=".06;.22;.06" dur="2.6s" begin="{i * 0.25:.2f}s" repeatCount="indefinite"/></circle>'
            if r in ("SS", "S")
            else ""
        )
        body.append(
            f"<g>{appear(dly, 0.5, 10)}"
            f'<rect x="{x + 4:.1f}" y="54" width="{cw - 8:.1f}" height="128" rx="14" fill="{col}" fill-opacity=".06" '
            f'stroke="{col}" stroke-opacity=".4"/>{glow}'
            f"<g>{float_anim}{icon('trophy', cx - 17, 70, col, 34)}</g>"
            f"{icon(ico, x + 12, 62, MUTED, 13)}"
            f'<text x="{cx:.1f}" y="134" text-anchor="middle" font-family="{FONT}" font-weight="800" font-size="18" '
            f'fill="{col}">{r}</text>'
            f'<text x="{cx:.1f}" y="154" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{INK}">'
            f"{escape(label)}</text>"
            f'<text x="{cx:.1f}" y="170" text-anchor="middle" font-family="{FONT}" font-size="11" fill="{MUTED}">'
            f"{escape(str(value))}</text></g>"
        )
    return card(h, "".join(body), dots(W, h) + aurora_defs())


def main():
    login, outdir = sys.argv[1], Path(sys.argv[2])
    d = sample() if "--sample" in sys.argv else fetch(login)
    outdir.mkdir(parents=True, exist_ok=True)
    updated = datetime.now(IST).strftime("%d %b %H:%M IST")
    (outdir / "stats.svg").write_text(render_stats(d, updated), encoding="utf-8")
    (outdir / "trophies.svg").write_text(render_trophies(d), encoding="utf-8")
    cur, best = streaks(d["days"])
    data = {
        "updated": updated,
        "total": d["total"],
        "current_streak": cur,
        "longest_streak": best,
        "repos": d["repos"],
        "stars": d["stars"],
        "days": d["days"],
        "languages": [
            {"name": n, "bytes": sz, "color": c} for n, (sz, c) in sorted(d["langs"].items(), key=lambda kv: -kv[1][0])
        ],
        "trophies": [
            {"label": lab, "value": v, "steps": list(st), "rank": rank(v, st)[0]} for lab, v, st, _ in trophy_items(d)
        ],
    }
    (outdir / "data.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    print(f"{outdir}: {d['total']} contributions, {d['repos']} public repos, {len(d['langs'])} languages")


if __name__ == "__main__":
    main()
