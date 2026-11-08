"""Builds the animated SVGs in assets/.

Fonts come from haashirkhan.com (Jost, IBM Plex). Text is converted to outlined paths,
because GitHub shows README SVGs as images and images can't load web fonts. The galaxy
is rendered by render.py and embedded as WebP, since an SVG image can't load
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


W = 880  # shared width of every full-width asset, matching the README tables

PHRASES = ["multi-agent AI platforms", "cloud infrastructure", "automation"]


def typing(t):
    w, h, size = W, 52, 22
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


def strip(t, index, label, w=W, h=56):
    """Section heading: index, tracked label, hairline."""
    idx, _ = text_path(index, JOST, 13, 28, 34, tracking=0.2)
    lab, lw = text_path(label, JOST, 13, 84, 34, tracking=0.32)
    body = (
        f'<path d="{idx}" fill="{t["accent"]}"/><path d="{lab}" fill="{t["ink"]}" fill-opacity="{t["dim"]}"/>'
        f'<rect x="{num(100 + lw)}" y="29" width="{num(w - 128 - lw)}" height="1" fill="{t["ink"]}" fill-opacity="{t["line"]}"/>'
    )
    return svg(w, h, body, "", label.title())


# Each project is a world, tinted after the site's planet accents.
PROJECTS = [
    {"slug": "autodocs", "kind": "gas", "tint": "#D2AD86", "seed": 3},
    {"slug": "nfl-moe", "kind": "rock", "tint": "#D48A62", "seed": 5},
    {"slug": "ploggo", "kind": "rock", "tint": "#8FB3D4", "seed": 8},
    {"slug": "discover-me", "kind": "gas", "tint": "#86A8E0", "seed": 12},
    {"slug": "texchange", "kind": "gas", "tint": "#DCCAA0", "seed": 21},
]


CHANNELS = [
    ("01", "WEB", "haashirkhan.com"),
    ("02", "LINKEDIN", "in/haashir-khan"),
    ("03", "EMAIL", "haashirk2003@gmail.com"),
]


def channel(t, i):
    w, h = 288, 80
    ch, label, value = CHANNELS[i]
    ink = t["ink"]
    c, cw = text_path(f"CH {ch}", MONO, 12, 18, 30, tracking=0.08)
    lab, _ = text_path(label, JOST, 11, 18 + cw + 14, 30, tracking=0.32)
    val, _ = text_path(value, SANS, 17, 18, 60)
    bars = "".join(
        f'<rect class="b" x="{250 + k * 7}" y="{30 - 5 - k * 4}" width="3" height="{5 + k * 4}" fill="{ink}" style="animation-delay:{k * 0.5 + i * 0.3:.1f}s"/>'
        for k in range(4)
    )
    body = (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="3" fill="{t["bg"]}" stroke="{ink}" stroke-opacity="{t["line"]}"/>'
        f'<path d="{c}" fill="{t["accent"]}"/><path d="{lab}" fill="{ink}" fill-opacity="{t["dim"]}"/><path d="{val}" fill="{ink}"/>' + bars
    )
    style = ".b { opacity: .35; animation: sig 3.2s ease-in-out infinite; } @keyframes sig { 0%,100% { opacity: .25 } 50% { opacity: .85 } }"
    return svg(w, h, body, style, f"{label.title()}: {value}")


def footer(t):
    w, h = W, 150
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
        + " .drift { animation: drift 60s linear infinite; } @keyframes drift { from { transform: translate(40px, 78px) } to { transform: translate(840px, 48px) } }"
        " .tilt { animation: tilt 12s ease-in-out infinite alternate; } @keyframes tilt { from { transform: rotate(-8deg) } to { transform: rotate(6deg) } }"
        " .beacon { animation: beacon 4s ease-in-out infinite; } @keyframes beacon { 0%,100% { opacity: .2 } 50% { opacity: 1 } }"
        " @media (prefers-reduced-motion: reduce) { .drift { transform: translate(440px, 64px) } }"
    )
    body = (
        f'<rect width="{w}" height="{h}" fill="{t["bg"]}" fill-opacity="0"/>'
        + stars(rng, t, 0, 0, w, 110, 64)
        + f'<rect x="0" y="112" width="{w}" height="1" fill="{ink}" fill-opacity="{t["line"]}"/>'
        + sat + f'<path d="{end}" fill="{ink}" fill-opacity="{t["dim"]}"/>'
    )
    return svg(w, h, body, style, "A satellite drifting past. End of transmission.")


BUILDS = {
    "header": header,
    "typing": typing,
    "orbit": lambda t: strip(t, "01", "ORBIT"),
    "stack": lambda t: strip(t, "02", "STACK"),
    "launched": lambda t: strip(t, "03", "LAUNCHED"),
    "activity": lambda t: strip(t, "05", "ACTIVITY"),
    "comms": lambda t: strip(t, "06", "COMMS"),
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
    # Small planet icons for the project grid in the README.
    for p in PROJECTS:
        Image.fromarray((render.planet(48, p["kind"], p["tint"], p["seed"]) * 255).astype("uint8"), "RGBA").save(OUT / f"planet-{p['slug']}.png", optimize=True)
        total += (OUT / f"planet-{p['slug']}.png").stat().st_size
    print(f"total {total / 1024:.0f} KB")
