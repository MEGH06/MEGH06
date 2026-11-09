"""Generate every custom SVG used by the profile README.

One design language: near-black background, off-white text, a single acid-lime
accent, monospace labels, HUD corner ticks. No emoji.

Usage (from repo root): python tools/gen_svgs.py
"""
import html
import json
import math
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = json.loads((ROOT / "content.json").read_text(encoding="utf-8"))

BG = "#0a0a0a"
PANEL = "#0f0f0f"
LINE = "#232323"
TEXT = "#ededed"
MUTED = "#8a8a8a"
DIM = "#4a4a4a"
ACCENT = "#c6ff00"

SANS = "'Inter','Segoe UI','Helvetica Neue',Arial,sans-serif"
MONO = "ui-monospace,'SFMono-Regular','JetBrains Mono',Menlo,Consolas,monospace"


def esc(s):
    return html.escape(str(s), quote=True)


def wrap(text, width):
    lines, cur = [], ""
    for word in text.split():
        if cur and len(cur) + 1 + len(word) > width:
            lines.append(cur)
            cur = word
        else:
            cur = f"{cur} {word}".strip()
    if cur:
        lines.append(cur)
    return lines


def corners(x, y, w, h, n=14, color=ACCENT):
    """HUD-style corner ticks around a rectangle."""
    p = []
    for cx, cy, dx, dy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        p.append(f"M{cx} {cy + dy * n}V{cy}H{cx + dx * n}")
    return f'<path d="{"".join(p)}" fill="none" stroke="{color}" stroke-width="2"/>'


def svg(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(label)}">\n{body}\n</svg>\n')


# --------------------------------------------------------------------------- hero
def hero():
    W, H = 1200, 440
    random.seed(7)
    out = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>']
    out.append(f"""<defs>
  <clipPath id="floor"><rect x="540" y="150" width="{W - 540}" height="{H - 150}"/></clipPath>
  <linearGradient id="fade" x1="540" x2="820" y1="0" y2="0" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="1"/>
  </linearGradient>
  <mask id="m"><rect x="540" y="0" width="{W}" height="{H}" fill="url(#fade)"/></mask>
</defs>
<style>
  .blink {{ animation: b 1.1s steps(1) infinite; }}
  @keyframes b {{ 50% {{ opacity: 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>""")

    # perspective floor grid
    vp = (900, 120)
    g = []
    for bx in range(-900, 2800, 110):
        g.append(f"M{vp[0]} {vp[1]}L{bx} {H}")
    for k in range(1, 14):
        y = 150 + (k ** 2) * 1.75
        if y > H:
            break
        g.append(f"M540 {y:.1f}H{W}")
    out.append(f'<g mask="url(#m)" clip-path="url(#floor)"><path d="{"".join(g)}" stroke="#1b1b1b" stroke-width="1" fill="none"/></g>')
    out.append(f'<path d="M560 150H{W - 20}" stroke="{LINE}" stroke-width="1" mask="url(#m)"/>')

    # camera trajectory
    pts = []
    N = 120
    for i in range(N + 1):
        t = i / N
        x = 660 + 470 * t
        y = 330 - 90 * t + 38 * math.sin(2 * math.pi * 1.3 * t)
        pts.append((t, x, y))
    d = "M" + "L".join(f"{x:.1f} {y:.1f}" for _, x, y in pts)
    dur = 9
    out.append(f'<path id="traj" d="{d}" fill="none" stroke="{DIM}" stroke-width="1" stroke-dasharray="3 5" mask="url(#m)"/>')
    out.append(f'<path d="{d}" fill="none" stroke="{ACCENT}" stroke-width="2" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1">'
               f'<animate attributeName="stroke-dashoffset" values="1;0;0" keyTimes="0;0.92;1" dur="{dur}s" repeatCount="indefinite"/></path>')

    # landmarks that light up as the camera passes them
    marks = []
    for _ in range(46):
        t = random.uniform(0.03, 0.97)
        i = int(t * N)
        _, x, y = pts[i]
        side = random.choice((-1, 1))
        x += random.uniform(-25, 25)
        y += side * random.uniform(22, 80) - random.uniform(0, 60) * (side < 0)
        if x < 600 or y < 160 or y > H - 15:
            continue
        tt = t * 0.92
        k1, k2 = max(tt, 0.001), min(tt + 0.03, 0.999)
        size = random.choice((2, 2, 3))
        marks.append(
            f'<g transform="translate({x:.1f} {y:.1f})" opacity="0.18">'
            f'<path d="M-{size + 3} 0H{size + 3}M0 -{size + 3}V{size + 3}" stroke="{ACCENT}" stroke-width="1"/>'
            f'<animate attributeName="opacity" values="0.18;0.18;1;0.55;0.55" keyTimes="0;{k1:.3f};{k2:.3f};0.97;1" dur="{dur}s" repeatCount="indefinite"/></g>')
    out.extend(marks)

    # camera frustum riding the trajectory
    out.append(f'<g><path d="M0 0L26 -14V14Z" fill="{ACCENT}" fill-opacity="0.12" stroke="{ACCENT}" stroke-width="1.5"/>'
               f'<circle r="3" fill="{ACCENT}"/>'
               f'<animateMotion dur="{dur}s" repeatCount="indefinite" rotate="auto" keyPoints="0;1;1" keyTimes="0;0.92;1" calcMode="linear">'
               f'<mpath href="#traj"/></animateMotion></g>')

    # HUD readout
    out.append(f'<g font-family="{MONO}" font-size="12" fill="{MUTED}">'
               f'<circle class="blink" cx="{W - 196}" cy="46" r="4" fill="{ACCENT}"/>'
               f'<text x="{W - 184}" y="50" fill="{ACCENT}">VIO // TRACKING</text>'
               f'<text x="{W - 184}" y="70">cam + imu fusion</text>'
               f'<text x="{W - 184}" y="90">landmarks: live</text></g>')

    # identity block
    h = DATA["hero"]
    out.append(f'<text x="64" y="78" font-family="{MONO}" font-size="15" fill="{ACCENT}">{esc(h["kicker"])}</text>')
    out.append(f'<text x="60" y="182" font-family="{SANS}" font-size="112" font-weight="800" fill="{TEXT}" letter-spacing="-3">{esc(h["first"])}</text>')
    out.append(f'<text x="60" y="282" font-family="{SANS}" font-size="112" font-weight="800" fill="{TEXT}" letter-spacing="-3">{esc(h["last"])}<tspan fill="{ACCENT}">.</tspan></text>')
    out.append(f'<text x="64" y="326" font-family="{MONO}" font-size="15" fill="{MUTED}" letter-spacing="2">{esc(h["domains"])}</text>')
    x = 64
    for num, lab in h["stats"]:
        out.append(f'<text x="{x}" y="388" font-family="{SANS}" font-size="34" font-weight="700" fill="{ACCENT}">{esc(num)}</text>')
        out.append(f'<text x="{x}" y="410" font-family="{MONO}" font-size="12" fill="{MUTED}" letter-spacing="1.5">{esc(lab)}</text>')
        x += 150
    out.append(corners(14, 14, W - 28, H - 28, 18))
    (ASSETS / "hero.svg").write_text(svg(W, H, "\n".join(out), f'{h["first"]} {h["last"]}: {h["domains"]}'), encoding="utf-8")


# --------------------------------------------------------------------------- project cards
def card(p):
    W, H = 600, 270
    o = [f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{PANEL}" stroke="{LINE}"/>']
    o.append(corners(10, 10, W - 20, H - 20, 12))
    o.append(f'<text x="34" y="52" font-family="{MONO}" font-size="12" fill="{ACCENT}" letter-spacing="1.5">{esc(p["label"].upper())}</text>')
    o.append(f'<text x="32" y="96" font-family="{SANS}" font-size="34" font-weight="800" fill="{TEXT}" letter-spacing="-0.5">{esc(p["name"])}</text>')
    y = 130
    for line in wrap(p["desc"], 64)[:3]:
        o.append(f'<text x="34" y="{y}" font-family="{SANS}" font-size="16" fill="{MUTED}">{esc(line)}</text>')
        y += 23
    x = 34
    for tag in p["stack"]:
        w = len(tag) * 7.6 + 20
        if x + w > W - 110:
            break
        o.append(f'<rect x="{x}" y="212" width="{w:.0f}" height="26" rx="5" fill="none" stroke="{LINE}"/>'
                 f'<text x="{x + 10}" y="229.5" font-family="{MONO}" font-size="12.5" fill="{TEXT}">{esc(tag)}</text>')
        x += w + 8
    o.append(f'<text x="{W - 34}" y="230" text-anchor="end" font-family="{MONO}" font-size="13" fill="{ACCENT}">{esc(p.get("cta", "open"))} &#8599;</text>')
    return svg(W, H, "\n".join(o), f'{p["name"]}: {p["desc"]}')


# --------------------------------------------------------------------------- capability grid
def capabilities():
    caps = DATA["capabilities"]
    cols, cw, ch, pad = 3, 386, 170, 14
    rows = math.ceil(len(caps) / cols)
    W, H = cols * cw + (cols + 1) * pad, rows * ch + (rows + 1) * pad
    o = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>']
    for i, c in enumerate(caps):
        x = pad + (i % cols) * (cw + pad)
        y = pad + (i // cols) * (ch + pad)
        o.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{cw - 1}" height="{ch - 1}" rx="10" fill="{PANEL}" stroke="{LINE}"/>')
        o.append(f'<text x="{x + 24}" y="{y + 40}" font-family="{MONO}" font-size="13" fill="{ACCENT}">{i + 1:02d}</text>')
        o.append(f'<text x="{x + 24}" y="{y + 74}" font-family="{SANS}" font-size="23" font-weight="800" fill="{TEXT}">{esc(c["title"])}</text>')
        ly = y + 104
        for line in wrap(c["desc"], 44)[:3]:
            o.append(f'<text x="{x + 24}" y="{ly}" font-family="{MONO}" font-size="12.5" fill="{MUTED}">{esc(line)}</text>')
            ly += 20
    (ASSETS / "capabilities.svg").write_text(
        svg(W, H, "\n".join(o), "What I do: " + ", ".join(c["title"] for c in caps)), encoding="utf-8")


# --------------------------------------------------------------------------- trophy leaderboard
def trophies():
    rows = DATA["trophies"]
    W, rh, top = 1200, 46, 70
    H = top + len(rows) * rh + 30
    o = [f'<rect width="{W}" height="{H}" rx="14" fill="{BG}"/>', corners(14, 14, W - 28, H - 28, 16)]
    o.append(f'<g font-family="{MONO}" font-size="12" fill="{DIM}" letter-spacing="1.5">'
             f'<text x="48" y="52">RESULT</text><text x="260" y="52">EVENT</text><text x="{W - 48}" y="52" text-anchor="end">PROJECT</text></g>')
    for i, (result, event, project) in enumerate(rows):
        y = top + i * rh
        o.append(f'<path d="M40 {y}H{W - 40}" stroke="{LINE}"/>')
        win = result.lower() == "winner"
        o.append(f'<text x="48" y="{y + 30}" font-family="{MONO}" font-size="14" font-weight="700" fill="{ACCENT if win else TEXT}">{esc(result.upper())}</text>')
        o.append(f'<text x="260" y="{y + 30}" font-family="{SANS}" font-size="17" fill="{TEXT}">{esc(event)}</text>')
        o.append(f'<text x="{W - 48}" y="{y + 30}" text-anchor="end" font-family="{MONO}" font-size="14" fill="{MUTED}">{esc(project)}</text>')
    (ASSETS / "trophies.svg").write_text(svg(W, H, "\n".join(o), "Hackathon results"), encoding="utf-8")


# --------------------------------------------------------------------------- section divider
def divider(name, index):
    W, H = 1200, 64
    o = [f'<text x="2" y="40" font-family="{MONO}" font-size="14" fill="{ACCENT}">{index}</text>',
         f'<text x="44" y="40" font-family="{SANS}" font-size="24" font-weight="800" fill="#9a9a9a" letter-spacing="3">{esc(name.upper())}</text>',
         f'<path d="M{56 + len(name) * 19} 32H{W - 2}" stroke="#3a3a3a"/>']
    return svg(W, H, "\n".join(o), name)


if __name__ == "__main__":
    (ASSETS / "cards").mkdir(parents=True, exist_ok=True)
    hero()
    for p in DATA["projects"]:
        (ASSETS / "cards" / f'{p["slug"]}.svg').write_text(card(p), encoding="utf-8")
    capabilities()
    trophies()
    (ASSETS / "sections").mkdir(exist_ok=True)
    for i, name in enumerate(DATA["sections"], 1):
        (ASSETS / "sections" / f"{i:02d}.svg").write_text(divider(name, f"{i:02d}"), encoding="utf-8")
    print("SVGs written to", ASSETS)
