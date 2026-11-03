"""Shared SVG building blocks for the profile README and dashboard: palette, card frame, animations, logos, icons.
Standard library only, deterministic. Every animation is SMIL or CSS inside the SVG, so it plays where GitHub shows
the image: no JavaScript, no web fonts, no remote files, no tracking. Elements start visible and animate in, so viewers
that do not play SVG animation (phone apps, previews) still show the finished picture.
"""

import base64
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
LOGOS = ASSETS / "logos"
W = 860
FONT = "'Segoe UI',Ubuntu,'Helvetica Neue',Arial,sans-serif"
MONO = "'JetBrains Mono','Cascadia Code',Consolas,'Liberation Mono',monospace"
BG0, BG1 = "#0b1020", "#131c38"
INK, MUTED = "#e6edf7", "#93a1bd"
VIOLET, CYAN, GREEN = "#8b5cf6", "#22d3ee", "#34d399"
BRONZE, SILVER, GOLD, ORANGE = "#cd7f32", "#c3cbd8", "#f5b301", "#ff5a36"
ROSE = "#f43f5e"

# "Naman" drawn in Unbounded ExtraBold (SIL Open Font License 1.1), converted to outlines at 64 px so it looks the
# same everywhere without loading a font: fontTools SVGPathPen over unbounded-latin-800-normal.woff2. Width 300 px.
NAME_PATH = "M48.6 -10.6 44.4 -9.7V-48H58.8V0H40.1L14.3 -38.3L18.6 -39.2V0H4.2V-48H23.4Z M98.9 0 97.2 -13.1 99 -18.3 97.2 -23.5 98.9 -36.7H114.2L111.7 -18.4L114.2 0ZM102.2 -18.3Q101.4 -12.5 98.8 -8.1Q96.3 -3.7 92.2 -1.3Q88.1 1.1 82.9 1.1Q77.6 1.1 73.5 -1.3Q69.4 -3.8 67.1 -8.2Q64.8 -12.5 64.8 -18.3Q64.8 -24.2 67.1 -28.6Q69.4 -33 73.5 -35.4Q77.6 -37.8 82.9 -37.8Q88.1 -37.8 92.2 -35.4Q96.3 -33 98.9 -28.6Q101.5 -24.3 102.2 -18.3ZM79.6 -18.3Q79.6 -15.9 80.6 -14Q81.6 -12.2 83.4 -11.1Q85.2 -10 87.5 -10Q89.9 -10 92 -11.1Q94.2 -12.2 95.9 -14Q97.5 -15.9 98.3 -18.3Q97.5 -20.7 95.9 -22.6Q94.2 -24.5 92 -25.6Q89.9 -26.7 87.5 -26.7Q85.2 -26.7 83.4 -25.6Q81.6 -24.5 80.6 -22.6Q79.6 -20.7 79.6 -18.3Z M118.2 -36.7H132.9L135.4 -21.5V0H120.7V-23.7ZM147.7 -37.8Q152.8 -37.8 156.4 -35.6Q160 -33.5 161.9 -29.7Q163.8 -25.8 163.8 -20.6V0H149.1V-18.5Q149.1 -22.1 147.4 -24Q145.7 -25.9 142.6 -25.9Q140.4 -25.9 138.7 -24.9Q137.1 -23.9 136.2 -22Q135.4 -20.2 135.4 -17.5L130.9 -19.8Q131.8 -25.8 134.2 -29.8Q136.6 -33.7 140.1 -35.7Q143.6 -37.8 147.7 -37.8ZM176.1 -37.8Q181.2 -37.8 184.8 -35.6Q188.4 -33.5 190.3 -29.7Q192.2 -25.8 192.2 -20.6V0H177.5V-18.5Q177.5 -22.1 175.8 -24Q174.1 -25.9 171 -25.9Q168.8 -25.9 167.1 -24.9Q165.5 -23.9 164.6 -22Q163.8 -20.2 163.8 -17.5L159.4 -19.8Q160.2 -25.8 162.6 -29.8Q165 -33.7 168.5 -35.7Q172 -37.8 176.1 -37.8Z M231.1 0 229.4 -13.1 231.2 -18.3 229.4 -23.5 231.1 -36.7H246.3L243.9 -18.4L246.3 0ZM234.4 -18.3Q233.6 -12.5 231 -8.1Q228.4 -3.7 224.4 -1.3Q220.3 1.1 215 1.1Q209.7 1.1 205.6 -1.3Q201.5 -3.8 199.3 -8.2Q197 -12.5 197 -18.3Q197 -24.2 199.3 -28.6Q201.5 -33 205.6 -35.4Q209.7 -37.8 215 -37.8Q220.3 -37.8 224.4 -35.4Q228.4 -33 231 -28.6Q233.7 -24.3 234.4 -18.3ZM211.8 -18.3Q211.8 -15.9 212.8 -14Q213.8 -12.2 215.6 -11.1Q217.3 -10 219.6 -10Q222 -10 224.2 -11.1Q226.4 -12.2 228 -14Q229.7 -15.9 230.5 -18.3Q229.7 -20.7 228 -22.6Q226.4 -24.5 224.2 -25.6Q222 -26.7 219.6 -26.7Q217.3 -26.7 215.6 -25.6Q213.8 -24.5 212.8 -22.6Q211.8 -20.7 211.8 -18.3Z M250.4 -36.7H265L267.5 -21.5V0H252.9V-23.7ZM280.6 -37.8Q286 -37.8 289.7 -35.6Q293.4 -33.5 295.4 -29.7Q297.4 -25.8 297.4 -20.6V0H282.7V-18.5Q282.7 -22.1 280.8 -24Q278.9 -25.9 275.5 -25.9Q273 -25.9 271.2 -24.9Q269.4 -23.9 268.5 -22Q267.5 -20.2 267.5 -17.5L263.1 -19.8Q263.9 -25.8 266.5 -29.8Q269 -33.7 272.6 -35.7Q276.3 -37.8 280.6 -37.8Z"
NAME_W = 300


def appear(delay, dur=0.5, dy=0):
    """Fade (and slide up by dy) in after delay. Starts at once, so the element's own attributes stay the final,
    visible state: viewers that do not play SVG animation (phone apps, previews) still show everything."""
    t = delay + dur
    k = f'keyTimes="0;{delay / t:.3f};1" dur="{t:.2f}s" fill="freeze"'
    out = f'<animate attributeName="opacity" values="0;0;1" {k}/>'
    if dy:
        out += f'<animateTransform attributeName="transform" type="translate" values="0 {dy};0 {dy};0 0" {k}/>'
    return out


def card(h, body, defs=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG0}"/><stop offset="1" stop-color="{BG1}"/></linearGradient>
<filter id="blur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="38"/></filter>
<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="frame"><rect width="{W}" height="{h}" rx="18"/></clipPath>
{defs}
</defs>
<g clip-path="url(#frame)">
<rect width="{W}" height="{h}" fill="url(#bg)"/>
{body}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="18" fill="none" stroke="#ffffff" stroke-opacity=".08"/>
</svg>
"""


def blob(cx, cy, r, color, dx, dy, dur, op=0.45):
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}" opacity="{op}" filter="url(#blur)">'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;{dx} {dy};0 0" dur="{dur}s" '
        f'repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></circle>'
    )


def dots(w, h, step=28):
    return (
        f'<pattern id="dots" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1.2" fill="#ffffff" opacity=".07"/></pattern>'
    )


def typing(lines, x, y, size, color, slot=4.0, pid="ty", opacity=1.0):
    """Lines typed one after another: each types (35%), holds, deletes (15%), then the next one."""
    total = slot * len(lines)
    parts = []
    for i, line in enumerate(lines):
        width = round(len(line) * size * 0.6)  # monospace: one character is about 0.6 em
        a, b = i * slot / total, (i + 1) * slot / total
        k = [0, a, a + 0.35 * (b - a), b - 0.15 * (b - a), b, 1]
        k = [round(max(0, min(1, v)), 4) for v in k]
        # keep keyTimes strictly increasing at the ends
        times, vals = [], []
        for t, v in zip(k, [0, 0, width, width, 0, 0], strict=True):
            if times and t <= times[-1]:
                continue
            times.append(t)
            vals.append(v)
        if times[-1] != 1:
            times.append(1)
            vals.append(0)
        kt, kv = ";".join(map(str, times)), ";".join(map(str, vals))
        cur = ";".join(str(x + v + 2) for v in vals)
        parts.append(
            f'<clipPath id="{pid}{i}"><rect x="{x}" y="{y - size}" height="{size * 1.5}" width="{width if i == 0 else 0}">'
            f'<animate attributeName="width" dur="{total}s" repeatCount="indefinite" keyTimes="{kt}" values="{kv}"/>'
            f"</rect></clipPath>"
            f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" fill="{color}" '
            f'textLength="{width}" lengthAdjust="spacingAndGlyphs" clip-path="url(#{pid}{i})" opacity="{opacity}">{escape(line)}</text>'
            f'<rect y="{y - size * 0.85}" width="{max(2, size // 9)}" height="{size * 1.05}" fill="{color}" '
            f'x="{x + width + 2}" opacity="{1 if i == 0 else 0}">'
            f'<animate attributeName="x" dur="{total}s" repeatCount="indefinite" keyTimes="{kt}" values="{cur}"/>'
            f'<animate attributeName="opacity" dur="{total}s" repeatCount="indefinite" '
            f'keyTimes="0;{a};{b};1" values="0;1;0;0" calcMode="discrete"/>'
            f"</rect>"
        )
    return "".join(parts)


def medallion(cx, cy):
    """Three stacked layers (bronze, silver, gold) with data drops falling through them."""
    out = []
    layers = [(BRONZE, "BRONZE", 0), (SILVER, "SILVER", 1), (GOLD, "GOLD", 2)]
    for color, label, i in layers:
        y = cy - 70 + i * 62
        out.append(
            f'<g><rect x="{cx - 92}" y="{y}" width="184" height="42" rx="12" fill="{color}" fill-opacity=".14" '
            f'stroke="{color}" stroke-opacity=".75"/>'
            f'<text x="{cx}" y="{y + 27}" text-anchor="middle" font-family="{FONT}" font-weight="700" font-size="14" '
            f'letter-spacing="4" fill="{color}">{label}</text>'
            f'<animate attributeName="opacity" values=".55;1;.55" dur="3s" begin="{i * 0.6}s" repeatCount="indefinite"/>'
            f"</g>"
        )
    for dx, delay, col in [(-58, 0, CYAN), (0, 0.9, VIOLET), (58, 1.8, CYAN), (-29, 2.4, GREEN)]:
        out.append(
            f'<circle cx="{cx + dx}" cy="{cy - 100}" r="4" fill="{col}" filter="url(#glow)">'
            f'<animate attributeName="cy" values="{cy - 100};{cy + 110}" dur="3.6s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="3.6s" begin="{delay}s" '
            f'repeatCount="indefinite"/></circle>'
        )
    return "".join(out)


def wave(w, h, y, a, k, phase):
    """A filled ribbon: four soft humps along y, flipped by phase (+1 / -1)."""
    pts = [f"M0 {h}", f"L0 {y + a * phase:.0f}"]
    for i in range(1, 5):
        x = w * i / 4
        pts.append(f"Q{x - w / 8:.0f} {y - a * (1 if (i + k) % 2 else -1) * phase:.0f} {x:.0f} {y:.0f}")
    pts.append(f"L{w} {h} Z")
    return " ".join(pts)


def aurora(w, h):
    """Slow aurora ribbons, a twinkling constellation and a soft light sweep: the hero background."""
    out = []
    ribbons = [(h * 0.78, 34, 0.30, 13), (h * 0.88, 26, 0.22, 17), (h * 0.70, 20, 0.14, 21)]  # y, amplitude, opacity, s
    for k, (y, a, op, dur) in enumerate(ribbons):
        up, down = wave(w, h, y, a, k, 1), wave(w, h, y, a, k, -1)
        out.append(
            f'<path d="{up}" fill="url(#rib{k})" opacity="{op}"><animate attributeName="d" dur="{dur}s" '
            f'repeatCount="indefinite" values="{up};{down};{up}" calcMode="spline" '
            f'keySplines=".45 0 .55 1;.45 0 .55 1"/></path>'
        )
    # constellation on the right half: fixed points, faint links, twinkling stars
    pts = [
        (470, 46),
        (530, 92),
        (606, 58),
        (668, 118),
        (742, 70),
        (812, 132),
        (560, 160),
        (700, 196),
        (812, 40),
        (640, 236),
        (500, 216),
        (780, 250),
    ]
    for i, (x1, y1) in enumerate(pts):
        for x2, y2 in pts[i + 1 :]:
            if (x1 - x2) ** 2 + (y1 - y2) ** 2 < 95**2:
                out.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#ffffff" stroke-opacity=".07"/>')
    for i, (x, y) in enumerate(pts):
        out.append(
            f'<circle cx="{x}" cy="{y}" r="{1.6 + (i % 3) * 0.5}" fill="#ffffff" opacity=".5">'
            f'<animate attributeName="opacity" values=".15;.8;.15" dur="{2.6 + (i % 4) * 0.7:.1f}s" '
            f'begin="{(i * 0.37) % 2:.2f}s" repeatCount="indefinite"/></circle>'
        )
    # light sweep every 9 s
    out.append(
        f'<rect x="-300" y="0" width="220" height="{h}" fill="url(#sweep)" transform="skewX(-20)">'
        f'<animate attributeName="x" values="-300;{w + 300}" keyTimes="0;1" dur="9s" repeatCount="indefinite"/></rect>'
    )
    return "".join(out)


def aurora_defs():
    out = ""
    for k, (a, b) in enumerate([(VIOLET, CYAN), (CYAN, VIOLET), ("#ec4899", VIOLET)]):
        out += (
            f'<linearGradient id="rib{k}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{a}"/>'
            f'<stop offset="1" stop-color="{b}"/></linearGradient>'
        )
    out += (
        '<linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>'
        "</linearGradient>"
    )
    return out


def engineer_icon(x, y, color):
    """Data engineer mark (drawn, 20 x 20): a database with a flowing pipe arrow; the data dots travel through it."""
    return (
        f'<g fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">'
        f'<ellipse cx="{x + 7}" cy="{y + 3.5}" rx="6.5" ry="2.8"/>'
        f'<path d="M{x + 0.5} {y + 3.5}v11c0 1.6 2.9 2.8 6.5 2.8s6.5-1.2 6.5-2.8v-11"/>'
        f'<path d="M{x + 0.5} {y + 9}c0 1.6 2.9 2.8 6.5 2.8s6.5-1.2 6.5-2.8"/>'
        f'<path d="M{x + 15.5} {y + 12}h4.5m-2-2.2 2.2 2.2-2.2 2.2"/></g>'
        f'<circle r="1.4" fill="{color}"><animateMotion dur="1.8s" repeatCount="indefinite" '
        f'path="M{x + 7} {y + 6} V{y + 16}"/><animate attributeName="opacity" values="0;1;0" dur="1.8s" repeatCount="indefinite"/></circle>'
    )


def pin(x, y, color):
    """Location pin (drawn, 14 x 20) that bobs gently, with a soft pulse on the ground."""
    return (
        f'<ellipse cx="{x + 7}" cy="{y + 21}" rx="4" ry="1.5" fill="{color}" opacity=".35">'
        f'<animate attributeName="rx" values="3;6;3" dur="2.2s" repeatCount="indefinite"/></ellipse>'
        f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -2.5;0 0" dur="2.2s" '
        f'repeatCount="indefinite"/><path d="M{x + 7} {y + 20}c-4.6-5.6-7-9.3-7-12.6a7 7 0 0 1 14 0c0 3.3-2.4 7-7 12.6z" '
        f'fill="{color}"/><circle cx="{x + 7}" cy="{y + 7.2}" r="2.6" fill="{BG0}"/></g>'
    )


def flow_path(pid, d):
    return (
        f'<path id="{pid}" d="{d}" fill="none" stroke="#ffffff" stroke-opacity=".14" stroke-width="2" stroke-dasharray="4 6">'
        f'<animate attributeName="stroke-dashoffset" values="20;0" dur="1s" repeatCount="indefinite"/></path>'
    )


def packet(pid, color, dur, begin):
    return (
        f'<circle r="4.5" fill="{color}" filter="url(#glow)"><animateMotion dur="{dur}s" begin="{begin}s" '
        f'repeatCount="indefinite" rotate="auto"><mpath href="#{pid}"/></animateMotion></circle>'
    )


def node(x, y, w, h, title, sub, color, delay=0.0):
    lines = sub.split("|")
    t = "".join(
        f'<text x="{x + w / 2}" y="{y + 44 + 15 * k}" text-anchor="middle" font-family="{FONT}" font-size="11.5" '
        f'fill="{MUTED}">{escape(s)}</text>'
        for k, s in enumerate(lines)
    )
    return (
        f"<g>{appear(delay, 0.6)}"
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" fill-opacity=".1" stroke="{color}" '
        f'stroke-opacity=".7"/><text x="{x + w / 2}" y="{y + 25}" text-anchor="middle" font-family="{FONT}" '
        f'font-weight="700" font-size="14" fill="{color}">{escape(title)}</text>{t}</g>'
    )


def logo(key, x, y, size, color, name):
    """The owner's logo file as an embedded image, else a monogram tile (no third-party artwork is drawn here)."""
    for ext, mime in (("svg", "image/svg+xml"), ("png", "image/png")):
        f = LOGOS / f"{key}.{ext}"
        if f.exists():
            data = base64.b64encode(f.read_bytes()).decode()
            return f'<image href="data:{mime};base64,{data}" x="{x}" y="{y}" width="{size}" height="{size}"/>'
    if key == "globe":
        k = size / 28
        return f'<g transform="translate({x} {y}) scale({k:.3f})">{globe(color)}</g>'
    initials = "".join(w[0] for w in name.replace("-", " ").split()[:2]).upper()
    return (
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size * 0.28:.1f}" fill="{color}" fill-opacity=".22"/>'
        f'<text x="{x + size / 2}" y="{y + size * 0.68}" text-anchor="middle" font-family="{FONT}" font-weight="800" '
        f'font-size="{size * 0.46:.1f}" fill="{color}">{escape(initials)}</text>'
    )


def globe(color):
    return (
        f'<g fill="none" stroke="{color}" stroke-width="1.8"><circle cx="14" cy="14" r="12"/>'
        f'<ellipse cx="14" cy="14" rx="5.5" ry="12"/><path d="M2 14h24M3.8 8h20.4M3.8 20h20.4"/>'
        f'<animateTransform attributeName="transform" type="rotate" values="0 14 14;8 14 14;0 14 14;-8 14 14;0 14 14" '
        f'dur="6s" repeatCount="indefinite"/></g>'
    )


def heart(color):
    return (
        f'<path d="M14 25s-10-6.2-10-13a5.6 5.6 0 0 1 10-3.4A5.6 5.6 0 0 1 24 12c0 6.8-10 13-10 13z" fill="{color}" '
        f'fill-opacity=".9"/>'
    )


def divider():
    h = 26
    flat = f"M0 13 Q {W / 8} 3 {W / 4} 13 T {W / 2} 13 T {3 * W / 4} 13 T {W} 13"
    flip = f"M0 13 Q {W / 8} 23 {W / 4} 13 T {W / 2} 13 T {3 * W / 4} 13 T {W} 13"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/>
<stop offset=".5" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient></defs>
<path d="{flat}" fill="none" stroke="url(#g)" stroke-width="2">
<animate attributeName="d" dur="5s" repeatCount="indefinite" values="{flat};{flip};{flat}"/></path>
<circle r="3.5" fill="{CYAN}"><animateMotion dur="5s" repeatCount="indefinite" path="M0 13 L{W} 13"/></circle>
</svg>
"""


def write(path, svg):
    """Write one SVG under assets/ and report its size."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg, encoding="utf-8")
    print(f"{path.relative_to(ROOT)}  {len(svg.encode()):,} bytes")
