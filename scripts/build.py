"""Builds the animated SVGs in assets/ from the palette and fonts of haashirkhan.com.

Text is converted to outlined paths, because GitHub renders README SVGs as images
and images can't load web fonts. Animation is CSS inside each SVG, and every file
switches it off under prefers-reduced-motion.

    pip install fonttools
    python scripts/build.py
"""
import random
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / "fonts"
OUT = ROOT / "assets"

# Colours from the site's src/ui.css and src/ui.ts. Light values are darkened for contrast on paper.
THEMES = {
    "dark": {
        "bg": "#000000", "panel": "#06080C", "text": "#E8E6E1", "dim": "#E8E6E1",
        "dimop": 0.62, "line": 0.12, "star": "#E8E6E1",
        "earth": "#8FB3D4", "moon": "#C2BFB7", "jupiter": "#D2AD86",
        "mars": "#D48A62", "saturn": "#DCCAA0", "neptune": "#86A8E0",
        "planet": ("#CFE0F2", "#5F86B0", "#132235", "#05070B"),
    },
    "light": {
        "bg": "#F4F2ED", "panel": "#FBFAF7", "text": "#1A1D24", "dim": "#1A1D24",
        "dimop": 0.66, "line": 0.14, "star": "#2B3140",
        "earth": "#3F6A93", "moon": "#6E6A61", "jupiter": "#8A6235",
        "mars": "#A2512A", "saturn": "#8A733F", "neptune": "#355FA8",
        "planet": ("#DCE8F5", "#5F86B0", "#2A4566", "#F4F2ED"),
    },
}

_fonts = {}


def font(name):
    if name not in _fonts:
        _fonts[name] = TTFont(FONTS / f"{name}.woff")
    return _fonts[name]


JOST = "jost-latin-400-normal"
SANS = "ibm-plex-sans-latin-400-normal"
SANS_SEMI = "ibm-plex-sans-latin-600-normal"
MONO = "ibm-plex-mono-latin-400-normal"


def text_path(s, fname, size, x=0.0, y=0.0, tracking=0.0, anchor="start"):
    """Return (path d, width) for s set in fname at size px, baseline at y. tracking is in em."""
    f = font(fname)
    scale = size / f["head"].unitsPerEm
    cmap, glyphs, hmtx = f.getBestCmap(), f.getGlyphSet(), f["hmtx"]
    names = [cmap[ord(c)] for c in s]
    adv = [hmtx[n][0] * scale + tracking * size for n in names]
    width = sum(adv) - (tracking * size if names else 0)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    pen = SVGPathPen(glyphs, ntos=num)
    cx = x
    for n, a in zip(names, adv):
        glyphs[n].draw(TransformPen(pen, (scale, 0, 0, -scale, cx, y)))
        cx += a
    return pen.getCommands(), width


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } .rm-hide { display: none; } }"


def svg(w, h, body, style, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
        f"<title>{title}</title><style>{style} {REDUCED}</style>{body}</svg>\n"
    )


def stars(rng, w, h, n, color, avoid=None):
    """Static stars plus a twinkling subset. avoid is an (x0, y0, x1, y1) box kept clear for text."""
    out, twinkle = [], []
    while len(out) + len(twinkle) < n:
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        r = rng.choice([0.5, 0.6, 0.7, 0.8, 0.9, 1.1, 1.4])
        op = rng.uniform(0.25, 0.85)
        c = f'<circle cx="{num(x)}" cy="{num(y)}" r="{r}" opacity="{op:.2f}"'
        if rng.random() < 0.3:
            dur, delay = rng.uniform(5, 10), rng.uniform(0, 8)
            twinkle.append(f'{c} class="tw" style="animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s"/>')
        else:
            out.append(c + "/>")
    return f'<g fill="{color}">{"".join(out)}{"".join(twinkle)}</g>'


def header(t):
    w, h = 1200, 300
    rng = random.Random(20)
    name, nw = text_path("HAASHIR KHAN", JOST, 62, 80, 158, tracking=0.4)
    title, _ = text_path("AI & DEVOPS ENGINEER", JOST, 27, 84, 214, tracking=0.28)
    p0, p1, p2, p3 = t["planet"]
    style = (
        ".tw { animation: tw 7s ease-in-out infinite; }"
        "@keyframes tw { 0%,100% { opacity: .2 } 50% { opacity: .9 } }"
        ".shoot { opacity: 0; animation: shoot 16s linear infinite 3s; }"
        "@keyframes shoot { 0% { opacity: 0; transform: translate(0,0) }"
        " 1% { opacity: .8 } 6% { opacity: 0; transform: translate(-340px,150px) } 100% { opacity: 0; transform: translate(-340px,150px) } }"
        ".orbit { animation: spin 90s linear infinite; transform-origin: 1000px 150px; }"
        "@keyframes spin { to { transform: rotate(360deg) } }"
    )
    body = (
        f'<defs><radialGradient id="pg" cx=".32" cy=".3" r=".8">'
        f'<stop offset="0" stop-color="{p0}"/><stop offset=".45" stop-color="{p1}"/>'
        f'<stop offset=".8" stop-color="{p2}"/><stop offset="1" stop-color="{p3}"/></radialGradient>'
        f'<linearGradient id="sg" gradientUnits="userSpaceOnUse" x1="1110" y1="-24" x2="1000" y2="26"><stop offset="0" stop-color="{t["text"]}" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="{t["text"]}"/></linearGradient></defs>'
        f'<rect width="{w}" height="{h}" fill="{t["bg"]}"/>'
        + stars(rng, w, h, 150, t["star"], avoid=(60, 90, 80 + nw + 30, 245))
        + f'<g class="shoot rm-hide"><line x1="1110" y1="-24" x2="1000" y2="26" stroke="url(#sg)" stroke-width="1.4" stroke-linecap="round"/></g>'
        # Partial orbit arc and planet, the site's world-target motif.
        f'<g transform="translate(1000 150) rotate(-18) scale(1 .32) translate(-1000 -150)">'
        f'<circle cx="1000" cy="150" r="120" fill="none" stroke="{t["text"]}" stroke-opacity=".28" stroke-width="2.4" stroke-dasharray="420 400"/>'
        f'<g class="orbit"><circle cx="1120" cy="150" r="6" fill="{t["earth"]}"/></g></g>'
        f'<circle cx="1000" cy="150" r="46" fill="url(#pg)"/>'
        f'<path d="{name}" fill="{t["text"]}"/>'
        f'<path d="{title}" fill="{t["dim"]}" fill-opacity="{t["dimop"]}"/>'
        f'<rect x="84" y="238" width="64" height="1" fill="{t["earth"]}"/>'
    )
    return svg(w, h, body, style, "Haashir Khan, AI and DevOps Engineer")


PHRASES = ["multi-agent AI platforms", "cloud infrastructure", "automation"]


def typing(t):
    w, h, size = 520, 52, 22
    prompt, pw = text_path("$ building", MONO, size, 20, 34)
    f = font(MONO)
    cw = f["hmtx"][f.getBestCmap()[ord("a")]][0] * size / f["head"].unitsPerEm  # monospace advance
    x0 = 20 + pw + cw
    n, slot = len(PHRASES), 4.0
    total = n * slot
    css, groups = [], []
    for i, p in enumerate(PHRASES):
        d, pwid = text_path(p, MONO, size, x0, 34)
        k = len(p)
        a, b, c, e = (i * slot + v for v in (0, 1.6, 3.4, 3.9))  # type, hold, erase, gone (seconds)
        pc = lambda s: f"{s / total * 100:.2f}%"
        css.append(
            f"@keyframes r{i} {{ 0% {{ transform: scaleX(0) }} {pc(a)} {{ transform: scaleX(0); animation-timing-function: steps({k}, end) }}"
            f" {pc(b)} {{ transform: scaleX(1) }} {pc(c)} {{ transform: scaleX(1); animation-timing-function: steps({k}, end) }}"
            f" {pc(e)} {{ transform: scaleX(0) }} 100% {{ transform: scaleX(0) }} }}"
            f"@keyframes c{i} {{ 0% {{ transform: translateX(0); opacity: 0 }} {pc(max(a - 0.01, 0))} {{ opacity: 0 }} {pc(a)} {{ transform: translateX(0); opacity: 1; animation-timing-function: steps({k}, end) }}"
            f" {pc(b)} {{ transform: translateX({num(k * cw)}px) }} {pc(c)} {{ transform: translateX({num(k * cw)}px); animation-timing-function: steps({k}, end) }}"
            f" {pc(e)} {{ transform: translateX(0); opacity: 1 }} {pc(e + 0.01)} {{ opacity: 0 }} 100% {{ opacity: 0 }} }}"
            f".r{i} {{ transform-origin: {num(x0)}px 0; animation: r{i} {total}s infinite; }}"
            f".c{i} {{ animation: c{i} {total}s infinite; }}"
        )
        # Reduced motion: the first phrase stays fully typed, the rest are hidden.
        static = "" if i == 0 else ' class="rm-hide"'
        groups.append(
            f'<g{static}><clipPath id="k{i}"><rect class="r{i}" x="{num(x0)}" y="8" width="{num(k * cw + 1)}" height="38"/></clipPath>'
            f'<path d="{d}" fill="{t["earth"]}" clip-path="url(#k{i})"/>'
            f'<rect class="c{i} rm-hide" x="{num(x0)}" y="16" width="{num(cw * 0.55)}" height="23" fill="{t["text"]}" opacity="0"/></g>'
        )
    style = "".join(css)
    body = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="8" fill="{t["panel"]}" stroke="{t["text"]}" stroke-opacity="{t["line"]}"/>'
        f'<path d="{prompt}" fill="{t["dim"]}" fill-opacity="{t["dimop"]}"/>' + "".join(groups)
    )
    return svg(w, h, body, style, "Building multi-agent AI platforms, cloud infrastructure and automation")


def panel(t, w, h, label, accent):
    """Mission-control panel frame with a tracked Jost label, like the site's section kickers."""
    lab, lw = text_path(label, JOST, 13, 32, 42, tracking=0.32)
    return (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="14" fill="{t["panel"]}" stroke="{t["text"]}" stroke-opacity="{t["line"]}"/>'
        f'<circle cx="36" cy="37.5" r="3.5" fill="{accent}"/>'
        f'<path d="{lab}" fill="{accent}" transform="translate(14 0)"/>'
        f'<rect x="{num(60 + lw)}" y="37" width="{num(w - 92 - lw)}" height="1" fill="{t["text"]}" fill-opacity="{t["line"]}"/>'
    )


def current_orbit(t):
    w, h = 560, 240
    rng = random.Random(7)
    role, _ = text_path("AI Solutions Engineer Co-op", SANS_SEMI, 26, 32, 98)
    org, _ = text_path("Magna International  ·  since Aug 2026", SANS, 18, 32, 130)
    what, _ = text_path("Building multi-agent RAG platforms", SANS, 18, 32, 178)
    what2, _ = text_path("on Databricks with LangGraph.", SANS, 18, 32, 204)
    p0, p1, p2, p3 = t["planet"]
    cx, cy = 470, 172
    style = (
        ".tw { animation: tw 8s ease-in-out infinite; }"
        "@keyframes tw { 0%,100% { opacity: .2 } 50% { opacity: .8 } }"
        f".sat {{ animation: spin 24s linear infinite; transform-origin: {cx}px {cy}px; }}"
        "@keyframes spin { to { transform: rotate(360deg) } }"
    )
    body = (
        f'<defs><radialGradient id="og" cx=".32" cy=".3" r=".8">'
        f'<stop offset="0" stop-color="{p0}"/><stop offset=".45" stop-color="{p1}"/>'
        f'<stop offset=".8" stop-color="{p2}"/><stop offset="1" stop-color="{p3}"/></radialGradient>'
        f'<clipPath id="pc"><rect x="370" y="110" width="186" height="126"/></clipPath></defs>'
        + panel(t, w, h, "CURRENT ORBIT", t["earth"])
        + f'<g clip-path="url(#pc)">{stars(rng, 186, 126, 20, t["star"])}</g>'.replace("<g fill", '<g transform="translate(370 110)" fill', 1)
        + f'<g transform="translate({cx} {cy}) rotate(-14) scale(1 .34) translate({-cx} {-cy})">'
        f'<circle cx="{cx}" cy="{cy}" r="62" fill="none" stroke="{t["text"]}" stroke-opacity=".3" stroke-width="2.6"/>'
        f'<g class="sat"><circle cx="{cx + 62}" cy="{cy}" r="5" fill="{t["jupiter"]}"/></g></g>'
        f'<circle cx="{cx}" cy="{cy}" r="24" fill="url(#og)"/>'
        f'<path d="{role}" fill="{t["text"]}"/>'
        f'<path d="{org}" fill="{t["dim"]}" fill-opacity="{t["dimop"]}"/>'
        f'<path d="{what}{what2}" fill="{t["text"]}" fill-opacity=".9"/>'
    )
    return svg(w, h, body, style, "Current orbit: AI Solutions Engineer Co-op at Magna International, building multi-agent RAG platforms")


BUILDS = {"header": header, "typing": typing, "current-orbit": current_orbit}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in BUILDS.items():
        for theme, t in THEMES.items():
            p = OUT / f"{name}-{theme}.svg"
            p.write_text(fn(t), encoding="utf-8")
            print(f"{p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")
