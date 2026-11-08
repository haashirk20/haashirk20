"""Builds the animated SVGs in assets/.

Fonts come from haashirkhan.com (Jost, IBM Plex). Text is converted to outlined paths,
because GitHub shows README SVGs as images and images can't load web fonts. The galaxy
and moon are rendered by render.py and embedded as WebP, since an SVG image can't load
external files either. Animation is CSS inside each SVG, and every file turns it off
under prefers-reduced-motion.

    pip install fonttools numpy scipy pillow
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


BUILDS = {"header": header, "typing": typing, "current-orbit": current_orbit}

if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, fn in BUILDS.items():
        for theme, t in THEMES.items():
            p = OUT / f"{name}-{theme}.svg"
            p.write_text(fn(t), encoding="utf-8")
            print(f"{p.relative_to(ROOT)}  {p.stat().st_size / 1024:.1f} KB")
