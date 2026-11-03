"""Writes README.md from config/profile.yml. Every item is its own image with its own link and tooltip (title).

    python scripts/build_readme.py

GitHub strips scripts and hover effects from READMEs, so the README offers links and short tooltips; the full hover
cards, the Bengaluru map card and per-point chart tooltips live on the dashboard (scripts/build_dashboard.py).
"""

import html

import yaml

from build_readme_assets import slug
from svg_kit import ROOT

RAW = "https://raw.githubusercontent.com/{owner}/{owner}/output/{file}"


def t(text):
    return html.escape(str(text), quote=True)


def link_img(url, src, tip, alt, size=""):
    return f'<a href="{t(url)}" title="{t(tip)}"><img src="{t(src)}" {size}alt="{t(alt)}" title="{t(tip)}" /></a>'


def employer_links(line, cfg):
    """{key} in an about line -> the employer's logo badge, linked, with a tooltip."""
    for key, e in (cfg.get("employers") or {}).items():
        tip = f"{e['name']} · {e['info']}"
        html_ = (
            f'<a href="{t(e["url"])}" title="{t(tip)}"><img src="assets/badges/{t(key)}.svg" height="22" '
            f'alt="{t(e["name"])}" title="{t(tip)}" /></a>'
        )
        line = line.replace("{" + key + "}", html_)
    return line


def details(summary, src, alt):
    """A GitHub collapsible panel: one click opens a live detail card in place."""
    return [
        "<details>",
        f"<summary><b>{t(summary)}</b></summary>",
        "",
        f'<img src="{t(src)}" width="100%" alt="{t(alt)}" />',
        "",
        "</details>",
        "",
    ]


def build(cfg):
    idt, dash, owner = cfg["identity"], cfg["dashboard"], cfg["owner"]
    raw = lambda f: RAW.format(owner=owner, file=f)  # noqa: E731
    out = ['<div align="center">', ""]
    out.append(
        link_img(
            dash,
            "assets/hero/hero.svg",
            f"{idt['name']} · {idt['role']} · {idt['place']} · open the live dashboard",
            f"{idt['name']}, {idt['role']} in {idt['place']}. {idt['status']}.",
            'width="100%" ',
        )
    )
    out.append("")
    buttons = []
    for b in cfg["buttons"]:
        url = dash if b["url"] == "dashboard" else idt["map_url"] if b["url"] == "map" else b["url"]
        buttons.append(
            link_img(url, f"assets/buttons/{b['key']}.svg", b["tip"], b["tip"].split(" · ")[0], 'width="64" ')
        )
    out.append("&nbsp;&nbsp;\n".join(buttons))
    out += ["", "</div>", "", '<img src="assets/hero/divider.svg" width="100%" alt="" />', "", "### About me", ""]
    out += [f"- {employer_links(line, cfg)}" for line in cfg["about"]]
    p = cfg["project"]
    out += [
        "",
        "### Featured project",
        "",
        link_img(
            p["url"],
            "assets/project/lakehouse.svg",
            p["tip"],
            f"{p['title']}: sources into Bronze, Silver and Gold, "
            "a group view, dashboards and alerts, released from dev to test to prod",
            'width="100%" ',
        ),
        "",
        "| Repo | What it is |",
        "|---|---|",
    ]
    out += [f"| [**{r['name']}**]({r['url']}) | {r['about']} |" for r in p["repos"]]
    out += [
        "",
        p["note"],
        f"<sub>Hover any box for details on the [live dashboard]({dash}).</sub>",
        "",
        "### Skills & Tools",
        "",
    ]
    for g in cfg["skills"]:
        out.append(f'<img src="assets/skills/group-{slug(g["group"])}.svg" width="100%" alt="{t(g["group"])}" /><br>')
        out.append(
            "\n".join(
                link_img(
                    it["url"],
                    f"assets/skills/{slug(it['name'])}.svg",
                    f"{it['name']} · {it['info']}",
                    it["name"],
                    'height="36" ',
                )
                for it in g["items"]
            )
        )
        out.append("")
    out += [
        "### GitHub activity",
        "",
        link_img(
            f"{dash}#activity",
            raw("stats.svg"),
            "GitHub activity, refreshed every 3 hours: contributions and commits in the last 12 months, current and "
            "longest streak, public repositories, a 26-week matrix, weekly graph and languages. "
            "Open 'Activity details' below for every number, or click for the interactive dashboard.",
            "GitHub activity: contributions, streaks, repositories, matrix, graph and languages, refreshed every 3 hours",
            'width="100%" ',
        ),
        "",
        *details(
            "Activity details: busiest day and week, monthly totals, every language",
            raw("activity-details.svg"),
            "Activity details: summary, contributions per month and languages, refreshed every 3 hours",
        ),
        link_img(
            f"{dash}#trophies",
            raw("trophies.svg"),
            "GitHub trophies, ranked C → B → A → S → SS from live GitHub numbers: contributions, commits, streak, "
            "repositories, languages, pull requests, stars and years on GitHub. Open 'Trophy details' below for the "
            "next target of each one.",
            "GitHub trophies, ranked C to SS, refreshed every 3 hours",
            'width="100%" ',
        ),
        "",
        *details(
            "Trophy details: your rank and the next target for each trophy",
            raw("trophy-details.svg"),
            "Trophy details: rank, next target and thresholds for each trophy",
        ),
        f'<a href="https://github.com/{owner}" title="Contribution graph">',
        "<picture>",
        f'  <source media="(prefers-color-scheme: dark)" srcset="{raw("snake-dark.svg")}" />',
        f'  <source media="(prefers-color-scheme: light)" srcset="{raw("snake-light.svg")}" />',
        f'  <img src="{raw("snake-dark.svg")}" width="100%" alt="Contribution graph eaten by a snake" />',
        "</picture>",
        "</a>",
        "",
        "### Support me",
        "",
        "If my work helped you, you can support it here. Thank you!",
        "",
        '<div align="center">',
        "",
    ]
    out.append(
        "\n".join(
            link_img(s["url"], f"assets/support/{s['key']}.svg", f"{s['name']} · {s['sub']}", s["name"], 'width="270" ')
            for s in cfg["support"]
            if s["url"]
        )
    )
    out += [
        "",
        "</div>",
        "",
        '<img src="assets/hero/divider.svg" width="100%" alt="" />',
        "",
        '<div align="center">',
        "",
        link_img(
            dash,
            f"https://komarev.com/ghpvc/?username={owner}&label=PROFILE%20VISITORS&color=8b5cf6&style=for-the-badge",
            "Profile visitors, counted live",
            "Profile visitors",
        ),
        "",
        "<sub>Built from <code>config/profile.yml</code> by the scripts in this repo; live cards refresh every 3 hours. "
        "The visitor counter is komarev.com and only sees GitHub's image proxy, never you.</sub>",
        "",
        "</div>",
        "",
    ]
    return "\n".join(out)


def main():
    cfg = yaml.safe_load((ROOT / "config" / "profile.yml").read_text(encoding="utf-8"))
    (ROOT / "README.md").write_text(build(cfg), encoding="utf-8")
    print("README.md written")


if __name__ == "__main__":
    main()
