"""Builds the animated SVGs in assets/.

Fonts come from haashirkhan.com (Jost, IBM Plex). Text is converted to outlined paths,
because GitHub shows README SVGs as images and images can't load web fonts. The galaxy
and moon are rendered by render.py and embedded as WebP, since an SVG image can't load
external files either. Animation is CSS inside each SVG, and every file turns it off
under prefers-reduced-motion.

    pip install -r scripts/requirements.txt
    python scripts/build.py
"""
import base64
import io
import random
from pathlib import Path

import numpy as np
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image

import render

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / "fonts"
OUT = ROOT / "assets"

# Monochrome, with the site's Jupiter amber (#D2AD86) as the single accent.
# Light mode is a photographic negative, like an astronomer's glass plate.
THEMES = {
    "dark": {"bg": "#000000", "ink": "#EDEBE6", "dim": 0.56, "line": 0.13, "accent": "#D2AD86", "star": "#FFFFFF", "warm": "#E8B98C"},
    "light": {"bg": "#F2F0EB", "ink": "#111317", "dim": 0.62, "line": 0.16, "accent": "#8A6235", "star": "#111317", "warm": "#8A6235"},
}

_fonts = {}
JOST = "jost-latin-400-normal"
JOST_MED = "jost-latin-500-normal"
SANS = "ibm-plex-sans-latin-400-normal"
MONO = "ibm-plex-mono-latin-400-normal"


def font(name):
    if name not in _fonts:
        _fonts[name] = TTFont(FONTS / f"{name}.woff")
    return _fonts[name]


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


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


def webp(arr, quality=78):
    """Float array in [0, 1] (RGB or RGBA) to a base64 WebP data URI."""
    mode = "RGBA" if arr.shape[-1] == 4 else "RGB"
    buf = io.BytesIO()
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype("uint8"), mode).save(buf, "WEBP", quality=quality, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def hex_rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255


def plate(rgb, t):
    """Dark mode keeps the render; light mode prints it as a negative on paper."""
    if t is THEMES["dark"]:
        return rgb
    lum = rgb.mean(-1, keepdims=True)
    # The black hole stays dark in the negative, or it reads as a white hole.
    n = rgb.shape[0]
    yy, xx = np.mgrid[0:n, 0:n]
    core = (np.hypot(xx - n / 2, yy - n / 2) < render.R_HOLE * n / 2 * 0.96 * 0.98)[..., None]
    lum = np.where(core, 1.0, lum)
    return hex_rgb(t["bg"]) + (hex_rgb(t["ink"]) - hex_rgb(t["bg"])) * lum


REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } .rm-hide { display: none; } }"


def svg(w, h, body, style, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img">'
        f"<title>{title}</title><style>{style} {REDUCED}</style>{body}</svg>\n"
    )


TWINKLE = ".tw { animation: tw 8s ease-in-out infinite; } @keyframes tw { 0%,100% { opacity: .15 } 50% { opacity: .85 } }"


def stars(rng, t, x0, y0, w, h, n, avoid=()):
    """Specks of varied size and brightness, a few warm, about a quarter twinkling slowly."""
    out = []
    while len(out) < n:
        x, y = rng.uniform(x0, x0 + w), rng.uniform(y0, y0 + h)
        if any(a[0] < x < a[2] and a[1] < y < a[3] for a in avoid):
            continue
        r = rng.choice([0.4, 0.5, 0.5, 0.6, 0.7, 0.8, 1.0, 1.3])
        col = t["warm"] if rng.random() < 0.06 else t["star"]
        attrs = f'cx="{num(x)}" cy="{num(y)}" r="{r}" fill="{col}" opacity="{rng.uniform(0.2, 0.9):.2f}"'
        if rng.random() < 0.25:
            attrs += f' class="tw" style="animation-duration:{rng.uniform(6, 12):.1f}s;animation-delay:-{rng.uniform(0, 10):.1f}s"'
        out.append(f"<circle {attrs}/>")
    return "".join(out)


_galaxy = None


def header(t):
    global _galaxy
    if _galaxy is None:
        _galaxy = render.galaxy(1000)
    w, h = 1200, 460
    rng = random.Random(3)
    ink, line = t["ink"], t["line"]
    top_l, _ = text_path("TORONTO, CANADA", JOST, 13, 64, 52, tracking=0.32)
    top_r, _ = text_path("HAASHIRKHAN.COM", JOST, 13, 1136, 52, tracking=0.32, anchor="end")
    n1, _ = text_path("Haashir", JOST_MED, 108, 58, 218)
    n2, n2w = text_path("Khan.", JOST_MED, 108, 58, 322)
    role, rw = text_path("AI & DEVOPS ENGINEER", JOST, 26, 92, 384, tracking=0.3)
    style = (
        TWINKLE
        + ".spin { animation: spin 420s linear infinite; }"
        " @keyframes spin { to { transform: rotate(-360deg) } }"
        ".shoot { opacity: 0; animation: shoot 19s linear infinite 4s; }"
        " @keyframes shoot { 0% { opacity: 0; transform: translate(0,0) } 1% { opacity: .9 }"
        " 5% { opacity: 0; transform: translate(-260px,120px) } 100% { opacity: 0; transform: translate(-260px,120px) } }"
    )
    gal = webp(plate(_galaxy, t), 80)
    body = (
        f'<defs><radialGradient id="gm"><stop offset=".72" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>'
        f'<mask id="m" maskUnits="userSpaceOnUse" x="-600" y="-600" width="1200" height="1200"><circle r="580" fill="url(#gm)"/></mask>'
        f'<linearGradient id="veil"><stop offset="0" stop-color="{t["bg"]}" stop-opacity=".92"/><stop offset=".55" stop-color="{t["bg"]}" stop-opacity=".55"/>'
        f'<stop offset="1" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="sg" gradientUnits="userSpaceOnUse" x1="1120" y1="70" x2="1040" y2="106"><stop offset="0" stop-color="{ink}" stop-opacity="0"/><stop offset="1" stop-color="{ink}"/></linearGradient></defs>'
        f'<rect width="{w}" height="{h}" fill="{t["bg"]}"/>'
        + stars(rng, t, 0, 0, w, h, 320)
        # Tilted disk; the image spins inside the tilt, so it turns like a real disk seen at an angle.
        + f'<g transform="translate(840 268) rotate(-22) scale(1 .4)"><g mask="url(#m)"><g class="spin">'
        f'<image href="{gal}" x="-580" y="-580" width="1160" height="1160"/></g></g></g>'
        f'<rect width="700" height="{h}" fill="url(#veil)"/>'
        f'<g class="shoot rm-hide"><line x1="1120" y1="70" x2="1040" y2="106" stroke="url(#sg)" stroke-width="1.3" stroke-linecap="round"/></g>'
        # Editorial frame: hairline rule with captions, as in a magazine spread.
        f'<g fill="{ink}" fill-opacity="{t["dim"]}"><path d="{top_l}"/><path d="{top_r}"/></g>'
        f'<rect x="64" y="72" width="1072" height="1" fill="{ink}" fill-opacity="{line}"/>'
        f'<path d="{n1}{n2}" fill="{ink}"/>'
        f'<rect x="64" y="368" width="16" height="16" fill="{t["accent"]}"/>'
        f'<path d="{role}" fill="{ink}" fill-opacity=".82"/>'
    )
    return svg(w, h, body, style, "Haashir Khan, AI and DevOps Engineer")


PHRASES = ["multi-agent AI platforms", "cloud infrastructure", "automation"]


def typing(t):
    w, h, size = 520, 52, 22
    prompt, pw = text_path("$ building", MONO, size, 22, 34)
    f = font(MONO)
    cw = f["hmtx"][f.getBestCmap()[ord("a")]][0] * size / f["head"].unitsPerEm  # monospace advance
    x0 = 22 + pw + cw
    n, slot = len(PHRASES), 4.0
    total = n * slot
    css, groups = [], []
    for i, p in enumerate(PHRASES):
        d, _ = text_path(p, MONO, size, x0, 34)
        k = len(p)
        a, b, c, e = (i * slot + v for v in (0, 1.6, 3.4, 3.9))  # type, hold, erase, gone (seconds)

        def pc(s):
            return f"{s / total * 100:.2f}%"

        css.append(
            f"@keyframes r{i} {{ 0% {{ transform: scaleX(0) }} {pc(a)} {{ transform: scaleX(0); animation-timing-function: steps({k}, end) }}"
            f" {pc(b)} {{ transform: scaleX(1) }} {pc(c)} {{ transform: scaleX(1); animation-timing-function: steps({k}, end) }}"
            f" {pc(e)} {{ transform: scaleX(0) }} 100% {{ transform: scaleX(0) }} }}"
            f"@keyframes c{i} {{ 0% {{ transform: translateX(0); opacity: 0 }} {pc(max(a - 0.01, 0))} {{ opacity: 0 }}"
            f" {pc(a)} {{ transform: translateX(0); opacity: 1; animation-timing-function: steps({k}, end) }}"
            f" {pc(b)} {{ transform: translateX({num(k * cw)}px) }} {pc(c)} {{ transform: translateX({num(k * cw)}px); animation-timing-function: steps({k}, end) }}"
            f" {pc(e)} {{ transform: translateX(0); opacity: 1 }} {pc(e + 0.01)} {{ opacity: 0 }} 100% {{ opacity: 0 }} }}"
            f".r{i} {{ transform-origin: {num(x0)}px 0; animation: r{i} {total}s infinite; }}"
            f".c{i} {{ animation: c{i} {total}s infinite; }}"
        )
        # Reduced motion: the first phrase stays fully typed, the rest are hidden.
        static = "" if i == 0 else ' class="rm-hide"'
        groups.append(
            f'<g{static}><clipPath id="k{i}"><rect class="r{i}" x="{num(x0)}" y="8" width="{num(k * cw + 1)}" height="38"/></clipPath>'
            f'<path d="{d}" fill="{t["ink"]}" clip-path="url(#k{i})"/>'
            f'<rect class="c{i} rm-hide" x="{num(x0)}" y="16" width="{num(cw * 0.55)}" height="23" fill="{t["accent"]}" opacity="0"/></g>'
        )
    body = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="3" fill="{t["bg"]}" stroke="{t["ink"]}" stroke-opacity="{t["line"]}"/>'
        f'<path d="{prompt}" fill="{t["ink"]}" fill-opacity="{t["dim"]}"/>' + "".join(groups)
    )
    return svg(w, h, body, "".join(css), "Building multi-agent AI platforms, cloud infrastructure and automation")


def card(t, w, h, index, label):
    """Section card: sharp hairline frame, an index column, and a tracked label, like a magazine layout."""
    ink, line = t["ink"], t["line"]
    idx, _ = text_path(index, JOST, 13, 28, 48, tracking=0.2)
    lab, _ = text_path(label, JOST, 13, 84, 48, tracking=0.32)
    return (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="3" fill="{t["bg"]}" stroke="{ink}" stroke-opacity="{line}"/>'
        f'<rect x="64" y="1" width="1" height="{h - 2}" fill="{ink}" fill-opacity="{line}"/>'
        f'<path d="{idx}" fill="{t["accent"]}"/>'
        f'<path d="{lab}" fill="{ink}" fill-opacity="{t["dim"]}"/>'
    )


_moon = None


def current_orbit(t):
    global _moon
    if _moon is None:
        _moon = render.moon(440)
    w, h = 560, 260
    rng = random.Random(9)
    ink = t["ink"]
    title, _ = text_path("AI Solutions Engineer", JOST_MED, 32, 84, 112)
    org, _ = text_path("Co-op, Magna International", SANS, 18, 84, 146)
    d1, _ = text_path("Building multi-agent RAG platforms", SANS, 17, 84, 196)
    d2, _ = text_path("on Databricks with LangGraph.", SANS, 17, 84, 220)
    m = _moon.copy()
    if t is THEMES["light"]:
        # On paper the unlit side should vanish, leaving only the crescent.
        m[..., 3] *= np.clip((m[..., :3].mean(-1) - 0.06) * 4, 0, 1)
    moon_uri = webp(m, 76)
    body = (
        f'<defs><clipPath id="cc"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="3"/></clipPath></defs>'
        + card(t, w, h, "01", "CURRENT ORBIT")
        + f'<g clip-path="url(#cc)">{stars(rng, t, 360, 10, 200, 240, 30)}'
        f'<image href="{moon_uri}" x="436" y="-20" width="300" height="300"/></g>'
        f'<path d="{title}" fill="{ink}"/>'
        f'<path d="{org}" fill="{ink}" fill-opacity="{t["dim"]}"/>'
        f'<path d="{d1}{d2}" fill="{ink}" fill-opacity=".86"/>'
    )
    return svg(w, h, body, TWINKLE, "Current orbit: AI Solutions Engineer Co-op at Magna International, building multi-agent RAG platforms")


def wrap(s, fname, size, maxw):
    """Greedy word wrap by measured width."""
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and text_path(trial, fname, size)[1] > maxw:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


def strip(t, index, label, w=560, h=56):
    """Section heading: index, tracked label, hairline."""
    idx, _ = text_path(index, JOST, 13, 28, 34, tracking=0.2)
    lab, lw = text_path(label, JOST, 13, 84, 34, tracking=0.32)
    body = (
        f'<path d="{idx}" fill="{t["accent"]}"/><path d="{lab}" fill="{t["ink"]}" fill-opacity="{t["dim"]}"/>'
        f'<rect x="{num(100 + lw)}" y="29" width="{num(w - 128 - lw)}" height="1" fill="{t["ink"]}" fill-opacity="{t["line"]}"/>'
    )
    return svg(w, h, body, "", label.title())


EXPERIENCE = [
    ("AUG 2026 · PRESENT", "AI Solutions Engineer Co-op", "Magna International, Milton ON"),
    ("AUG 2025 · DEC 2025", "Automation and Systems Analyst Intern", "Perimeter Institute for Theoretical Physics"),
    ("MAY 2025 · AUG 2025", "Software, Cloud and DevOps Intern", "Perimeter Institute for Theoretical Physics"),
]


def mission_log(t):
    w, h, step = 560, 340, 84
    ink = t["ink"]
    parts = [card(t, w, h, "02", "MISSION LOG")]
    parts.append(f'<rect x="96" y="96" width="1" height="{2 * step + 8}" fill="{ink}" fill-opacity="{t["line"] * 2}"/>')
    for i, (dates, title, org) in enumerate(EXPERIENCE):
        y = 100 + i * step
        d, _ = text_path(dates, MONO, 12, 118, y + 4, tracking=0.08)
        ti, _ = text_path(title, JOST_MED, 21, 118, y + 30)
        o, _ = text_path(org, SANS, 15, 118, y + 52)
        if i == 0:
            parts.append(f'<circle class="pulse" cx="96.5" cy="{y}" r="9" fill="none" stroke="{t["accent"]}" stroke-width="1"/>')
        parts.append(f'<circle cx="96.5" cy="{y}" r="4" fill="{t["accent"] if i == 0 else t["bg"]}" stroke="{t["accent"] if i == 0 else ink}" stroke-opacity="{1 if i == 0 else 0.5}"/>')
        parts.append(
            f'<path d="{d}" fill="{t["accent"] if i == 0 else ink}" fill-opacity="{1 if i == 0 else t["dim"]}"/>'
            f'<path d="{ti}" fill="{ink}"/><path d="{o}" fill="{ink}" fill-opacity="{t["dim"]}"/>'
        )
    style = (
        ".pulse { transform-origin: 96.5px 100px; animation: pulse 4s ease-out infinite; }"
        " @keyframes pulse { 0% { transform: scale(.5); opacity: .8 } 100% { transform: scale(1.8); opacity: 0 } }"
    )
    return svg(w, h, "".join(parts), style, "Mission log: Magna International and two terms at Perimeter Institute")


# Each project is a world, tinted after the site's planet accents.
PROJECTS = [
    {
        "slug": "autodocs", "name": "AutoDocs", "year": "2026", "kind": "gas", "tint": "#D2AD86", "seed": 3,
        "pitch": "Turns asciinema terminal recordings into structured documentation with a fine-tuned Phi-4 pipeline. Mentored by the Linux Foundation and the Human Feedback Foundation.",
        "stack": "NEXT.JS · POSTGRESQL · PYTORCH · PHI-4",
        "repo": "https://github.com/CSC392-CSC492-Building-AI-ML-systems/AutoDocs-Winter2026",
        "demo": ("Demo video", "https://drive.google.com/file/d/1ssCTLpFQCOF0IWctK1j3NYFi1jjNiI9B/view"),
    },
    {
        "slug": "nfl-moe", "name": "NFL Mixture of Experts", "year": "2024", "kind": "rock", "tint": "#D48A62", "seed": 5,
        "pitch": "Predicts pass or run from pre-snap NFL Big Data Bowl 2025 data, with a gating network that weighs a CNN, an RNN and an MLP expert.",
        "stack": "PYTHON · PYTORCH · PANDAS",
        "repo": "https://github.com/ShishirAravindan/nfl-prediction-MoE",
        "demo": None,
    },
    {
        "slug": "ploggo", "name": "PlogGo", "year": "2025", "kind": "rock", "tint": "#8FB3D4", "seed": 8,
        "pitch": "Plogging app for web, iOS and Android that spots litter in your photos with a server-side detection model.",
        "stack": "REACT NATIVE · EXPO · FLASK · MONGODB · PYTORCH",
        "repo": "https://github.com/gdgutm/PlogGo",
        "demo": None,
    },
    {
        "slug": "discover-me", "name": "Discover Me", "year": "2025", "kind": "gas", "tint": "#86A8E0", "seed": 12,
        "pitch": "DeerHacks IV web app that matches travellers to destinations from a personality quiz and shows each place in Google Maps and Street View.",
        "stack": "NEXT.JS · REACT · OPENAI API · GOOGLE MAPS",
        "repo": "https://github.com/AviGhat/deerhacks2025",
        "demo": ("Live site", "https://deerhacks2025.vercel.app/"),
    },
    {
        "slug": "texchange", "name": "TexChange", "year": "2025", "kind": "gas", "tint": "#DCCAA0", "seed": 21,
        "pitch": "Anonymous text chat roulette. Socket.IO pairs strangers into private rooms and puts them back in the queue on a swap or a disconnect.",
        "stack": "REACT · EXPRESS · SOCKET.IO · DOCKER",
        "repo": "https://github.com/haashirk20/texchange",
        "demo": None,
    },
]

_planets = {}


def planet_uri(p, size=128):
    key = (p["slug"], size)
    if key not in _planets:
        _planets[key] = webp(render.planet(size, p["kind"], p["tint"], p["seed"]), 82)
    return _planets[key]


def project_card(t, p):
    w = 560
    ink = t["ink"]
    lines = wrap(p["pitch"], SANS, 15, 420)
    h = 128 + 21 * len(lines)
    name, _ = text_path(p["name"], JOST_MED, 24, 116, 52)
    year, _ = text_path(p["year"], MONO, 12, 532, 50, anchor="end")
    pitch = "".join(text_path(s, SANS, 15, 116, 84 + 21 * i)[0] for i, s in enumerate(lines))
    sy = 84 + 21 * len(lines) + 16
    stack, _ = text_path(p["stack"], MONO, 11.5, 116, sy, tracking=0.04)
    tag = ""
    if p["demo"]:
        dt, dw = text_path(p["demo"][0].upper(), JOST, 11, 532, sy, tracking=0.24, anchor="end")
        tag = f'<path d="{dt}" fill="{t["accent"]}"/><circle cx="{num(532 - dw - 12)}" cy="{sy - 4}" r="3" fill="{t["accent"]}"/>'
    body = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="3" fill="{t["bg"]}" stroke="{ink}" stroke-opacity="{t["line"]}"/>'
        f'<rect x="96" y="1" width="1" height="{h - 2}" fill="{ink}" fill-opacity="{t["line"]}"/>'
        f'<image href="{planet_uri(p, 112)}" x="20" y="22" width="56" height="56"/>'
        f'<path d="{name}" fill="{ink}"/><path d="{year}" fill="{ink}" fill-opacity="{t["dim"]}"/>'
        f'<path d="{pitch}" fill="{ink}" fill-opacity=".86"/>'
        f'<path d="{stack}" fill="{ink}" fill-opacity="{t["dim"]}"/>' + tag
    )
    return svg(w, h, body, "", f'{p["name"]}: {p["pitch"]}')


_core = None


def system_map(t):
    """The featured projects as planets orbiting a small galaxy core."""
    global _core
    if _core is None:
        g = render.galaxy(1000)
        _core = np.asarray(Image.fromarray((g * 255).astype("uint8")).resize((360, 360), Image.LANCZOS)) / 255
    w, h = 560, 400
    cx, cy, tilt = 318, 232, -8
    ink = t["ink"]
    rng = random.Random(14)
    core = webp(plate(_core, t), 78)
    css, orbits, bodies = [], [], []
    for i, p in enumerate(PROJECTS):
        rx = 84 + i * 31
        ry = rx * 0.36
        a = np.radians(tilt)
        x1, y1 = cx - rx * np.cos(a), cy - rx * np.sin(a)
        x2, y2 = cx + rx * np.cos(a), cy + rx * np.sin(a)
        path = f"M {num(x1)} {num(y1)} A {num(rx)} {num(ry)} {tilt} 1 0 {num(x2)} {num(y2)} A {num(rx)} {num(ry)} {tilt} 1 0 {num(x1)} {num(y1)} Z"
        start = (i * 37 + 10) % 100
        period = 70 + i * 28
        orbits.append(f'<path d="{path}" fill="none" stroke="{ink}" stroke-opacity="{t["line"] * 1.6}" stroke-width="1"/>')
        css.append(
            f".o{i} {{ offset-path: path('{path}'); offset-rotate: 0deg; offset-distance: {start}%; animation: o{i} {period}s linear infinite; }}"
            f" @keyframes o{i} {{ from {{ offset-distance: {start}% }} to {{ offset-distance: {start + 100}% }} }}"
        )
        s = 18 + (i % 3) * 4
        lab, _ = text_path(p["name"].upper(), JOST, 10.5, 0, -s / 2 - 8, tracking=0.22, anchor="middle")
        bodies.append(
            f'<g class="o{i}"><image href="{planet_uri(p, 64)}" x="{-s / 2}" y="{-s / 2}" width="{s}" height="{s}"/>'
            f'<path d="{lab}" fill="{ink}" fill-opacity=".8"/></g>'
        )
    body = (
        f'<defs><clipPath id="sc"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="3"/></clipPath>'
        f'<radialGradient id="cm"><stop offset=".6" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>'
        f'<mask id="cmk" maskUnits="userSpaceOnUse" x="-100" y="-100" width="200" height="200"><circle r="90" fill="url(#cm)"/></mask></defs>'
        + card(t, w, h, "04", "SYSTEM MAP")
        + f'<g clip-path="url(#sc)">{stars(rng, t, 66, 60, 490, 335, 70)}'
        f'<g transform="translate({cx} {cy}) rotate({tilt}) scale(1 .4)"><g mask="url(#cmk)"><g class="spin"><image href="{core}" x="-90" y="-90" width="180" height="180"/></g></g></g>'
        + "".join(orbits) + "".join(bodies) + "</g>"
    )
    style = TWINKLE + " .spin { animation: spin 240s linear infinite; } @keyframes spin { to { transform: rotate(-360deg) } } " + "".join(css)
    return svg(w, h, body, style, "System map: " + ", ".join(p["name"] for p in PROJECTS) + " orbiting a galaxy core")


# Core stack as three constellations. Positions are hand placed; anchor says which side the label sits on.
CONSTELLATIONS = [
    ("INTELLIGENCE", (110, 82), [("Python", 124, 128, "start"), ("PyTorch", 236, 110, "start"), ("LangGraph", 270, 178, "start"), ("Databricks", 150, 214, "start")],
     [(0, 1), (1, 2), (2, 3), (3, 0)]),
    ("INFRASTRUCTURE", (528, 82), [("AWS", 392, 124, "start"), ("Azure", 500, 140, "end"), ("Docker", 430, 206, "start"), ("Kubernetes", 512, 262, "end"), ("GitHub Actions", 516, 338, "end")],
     [(0, 1), (0, 2), (2, 3), (2, 4)]),
    ("CODE & DATA", (110, 290), [("TypeScript", 130, 330, "start"), ("Go", 250, 296, "start"), ("Java", 228, 380, "start"), ("PostgreSQL", 142, 410, "start")],
     [(0, 1), (1, 2), (2, 3), (3, 0)]),
]


def constellation(t):
    w, h = 560, 450
    ink = t["ink"]
    rng = random.Random(21)
    parts, names = [], []
    for title, (tx, ty), pts, links in CONSTELLATIONS:
        anchor = "end" if tx > 300 else "start"
        tp, _ = text_path(title, JOST, 11, tx, ty, tracking=0.32, anchor=anchor)
        names.append(f'<path d="{tp}" fill="{t["accent"]}"/>')
        for a, b in links:
            (_, x1, y1, _), (_, x2, y2, _) = pts[a], pts[b]
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{ink}" stroke-opacity=".22" stroke-width="1"/>')
        for name, x, y, side in pts:
            dur, delay = rng.uniform(5, 9), rng.uniform(0, 6)
            parts.append(
                f'<circle cx="{x}" cy="{y}" r="9" fill="url(#glow)" class="tw" style="animation-duration:{dur:.1f}s;animation-delay:-{delay:.1f}s"/>'
                f'<circle cx="{x}" cy="{y}" r="2.4" fill="{ink}"/>'
            )
            lx = x + 12 if side == "start" else x - 12
            lp, _ = text_path(name.upper(), JOST, 12.5, lx, y + 4.5, tracking=0.16, anchor=side)
            parts.append(f'<path d="{lp}" fill="{ink}" fill-opacity=".88"/>')
    body = (
        f'<defs><radialGradient id="glow"><stop offset="0" stop-color="{ink}" stop-opacity=".55"/><stop offset="1" stop-color="{ink}" stop-opacity="0"/></radialGradient></defs>'
        + card(t, w, h, "05", "CONSTELLATION")
        + stars(rng, t, 70, 64, 480, 376, 80)
        + "".join(names) + "".join(parts)
    )
    return svg(w, h, body, TWINKLE, "Core stack: Python, PyTorch, LangGraph, Databricks, AWS, Azure, Docker, Kubernetes, GitHub Actions, TypeScript, Go, Java, PostgreSQL")


CHANNELS = [
    ("01", "WEB", "haashirkhan.com"),
    ("02", "LINKEDIN", "linkedin.com/in/haashir-khan"),
    ("03", "EMAIL", "haashirk2003@gmail.com"),
]


def channel(t, i):
    w, h = 560, 72
    ch, label, value = CHANNELS[i]
    ink = t["ink"]
    c, _ = text_path(f"CH {ch}", MONO, 12, 28, 41, tracking=0.08)
    lab, _ = text_path(label, JOST, 11, 116, 30, tracking=0.32)
    val, _ = text_path(value, SANS, 18, 116, 54)
    bars = "".join(
        f'<rect class="b" x="{500 + k * 9}" y="{46 - 6 - k * 5}" width="4" height="{6 + k * 5}" fill="{ink}" style="animation-delay:{k * 0.5 + i * 0.3:.1f}s"/>'
        for k in range(4)
    )
    body = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="3" fill="{t["bg"]}" stroke="{ink}" stroke-opacity="{t["line"]}"/>'
        f'<rect x="96" y="1" width="1" height="{h - 2}" fill="{ink}" fill-opacity="{t["line"]}"/>'
        f'<path d="{c}" fill="{t["accent"]}"/><path d="{lab}" fill="{ink}" fill-opacity="{t["dim"]}"/><path d="{val}" fill="{ink}"/>' + bars
    )
    style = ".b { opacity: .35; animation: sig 3.2s ease-in-out infinite; } @keyframes sig { 0%,100% { opacity: .25 } 50% { opacity: .85 } }"
    return svg(w, h, body, style, f"{label.title()}: {value}")


def footer(t):
    w, h = 560, 150
    ink = t["ink"]
    rng = random.Random(30)
    end, _ = text_path("END OF TRANSMISSION", JOST, 11, w / 2, 134, tracking=0.36, anchor="middle")
    # A small satellite: body, two panels with cell lines, an antenna and a slow amber beacon.
    panel = lambda x: (
        f'<rect x="{x}" y="-7" width="30" height="14" fill="none" stroke="{ink}" stroke-opacity=".75"/>'
        + "".join(f'<line x1="{x + k * 7.5}" y1="-7" x2="{x + k * 7.5}" y2="7" stroke="{ink}" stroke-opacity=".35"/>' for k in (1, 2, 3))
    )
    sat = (
        f'<g class="drift"><g class="tilt">{panel(-44)}{panel(14)}'
        f'<line x1="-14" y1="0" x2="-8" y2="0" stroke="{ink}" stroke-opacity=".6"/><line x1="8" y1="0" x2="14" y2="0" stroke="{ink}" stroke-opacity=".6"/>'
        f'<rect x="-8" y="-9" width="16" height="18" rx="2" fill="{t["bg"]}" stroke="{ink}"/>'
        f'<line x1="0" y1="-9" x2="0" y2="-19" stroke="{ink}" stroke-opacity=".7"/>'
        f'<circle class="beacon" cx="0" cy="-20" r="2" fill="{t["accent"]}"/></g></g>'
    )
    style = (
        TWINKLE
        + " .drift { animation: drift 60s linear infinite; } @keyframes drift { from { transform: translate(40px, 78px) } to { transform: translate(520px, 52px) } }"
        " .tilt { animation: tilt 12s ease-in-out infinite alternate; } @keyframes tilt { from { transform: rotate(-8deg) } to { transform: rotate(6deg) } }"
        " .beacon { animation: beacon 4s ease-in-out infinite; } @keyframes beacon { 0%,100% { opacity: .2 } 50% { opacity: 1 } }"
        " @media (prefers-reduced-motion: reduce) { .drift { transform: translate(280px, 66px) } }"
    )
    body = (
        f'<rect width="{w}" height="{h}" fill="{t["bg"]}" fill-opacity="0"/>'
        + stars(rng, t, 0, 0, w, 110, 40)
        + f'<rect x="0" y="112" width="{w}" height="1" fill="{ink}" fill-opacity="{t["line"]}"/>'
        + sat + f'<path d="{end}" fill="{ink}" fill-opacity="{t["dim"]}"/>'
    )
    return svg(w, h, body, style, "A satellite drifting past. End of transmission.")


BUILDS = {
    "header": header,
    "typing": typing,
    "current-orbit": current_orbit,
    "mission-log": mission_log,
    "launched": lambda t: strip(t, "03", "LAUNCHED"),
    **{f"project-{p['slug']}": (lambda p: lambda t: project_card(t, p))(p) for p in PROJECTS},
    "system-map": system_map,
    "constellation": constellation,
    "activity": lambda t: strip(t, "07", "ACTIVITY"),
    "comms": lambda t: strip(t, "08", "COMMS"),
    **{f"channel-{i + 1}": (lambda i: lambda t: channel(t, i))(i) for i in range(len(CHANNELS))},
    "footer": footer,
}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    total = 0
    for name, fn in BUILDS.items():
        for theme, t in THEMES.items():
            p = OUT / f"{name}-{theme}.svg"
            p.write_text(fn(t), encoding="utf-8")
            total += p.stat().st_size
            print(f"{p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")
    print(f"total {total / 1024:.0f} KB")
