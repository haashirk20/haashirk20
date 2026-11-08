"""README graphics for haashirk20/personal_website. Colours and fonts are the site's own (src/ui.css): black
background, #E8E6E1 text and #D2AD86 amber, set in Jost, IBM Plex Sans and IBM Plex Mono."""
from kit import W, bars, box, fillrect, frame, head, hero, kicker, lines, text
from build import JOST, JOST_MED, MONO, SANS

THEMES = {
    "dark": {"bg": "#000000", "ink": "#E8E6E1", "dim": 0.62, "line": 0.18, "accent": "#D2AD86", "panel": "#161514"},
    "light": {"bg": "#F6F4EF", "ink": "#151412", "dim": 0.64, "line": 0.15, "accent": "#8A6640", "panel": "#ECE7DD"},
}

# World, section, flat colour for the sketch, radius, position.
WORLDS = [("Earth", "About", "#3D6FA8", 34, 600, 280), ("Moon", "Education", "#9C9890", 14, 690, 250),
          ("Jupiter", "Experience", "#C9A57E", 28, 790, 132), ("Mars", "Projects", "#B5583A", 15, 566, 150),
          ("Saturn", "Skills", "#D8C08E", 20, 680, 122), ("Neptune", "Contact", "#4C6FD6", 14, 770, 230)]


def worlds(t):
    """A flat map of the six worlds and the resume section each one holds. Not to scale."""
    out = [f'<rect x="520" y="40" width="320" height="320" rx="10" fill="{t["panel"]}"/>',
           text(t, "SIX WORLDS, SIX SECTIONS", JOST, 10, 540, 66, op=.75, tracking=0.24)[0]]
    for name, section, col, r, cx, cy in WORLDS:
        if name == "Saturn":
            out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{r * 1.9}" ry="{r * .5}" fill="none" stroke="{col}" stroke-width="3" stroke-opacity=".8"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{col}"/>')
        ty = cy + r + 16
        out.append(text(t, section, JOST_MED, 12.5, cx, ty, anchor="middle")[0])
        out.append(text(t, name.upper(), JOST, 9, cx, ty + 14, op=t["dim"], tracking=0.2, anchor="middle")[0])
    return "".join(out)


def g_hero(t):
    return hero(t, "PORTFOLIO  ·  WEBGL  ·  2026", "Personal website",
                "My resume as a real-time 3D solar system. Each section is a planet you can fly to.",
                [("6", "worlds"), ("9,096", "catalogued stars"), ("5", "test viewports")],
                "TypeScript · Three.js · GLSL · Vite · Playwright", figure=worlds)


def node(t, x, y, w, h, title, sub, accent=False, dim=False):
    return (box(t, x, y, w, h, accent=accent, op=.18 if dim else None)
            + text(t, title, JOST_MED, 14.5, x + 14, y + 26, op=.7 if dim else 1)[0]
            + lines(t, sub, MONO, 10.5, x + 14, y + 45, w - 28, 15, op=t["dim"])[0])


def line(t, x1, y1, x2, y2, label=None):
    out = f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{t["ink"]}" stroke-opacity=".4"/>'
    if label:
        out += text(t, label, MONO, 10, (x1 + x2) / 2, min(y1, y2) - 8, color=t["accent"], anchor="middle")[0]
    return out


def g_arch(t):
    h, y = head(t, "ARCHITECTURE", "The page works first, then WebGL fills it in.")
    y += 10
    out = [frame(t, 470), h]
    out.append(node(t, 40, y + 85, 150, 70, "main.ts", "entry point"))
    out.append(node(t, 260, y, 220, 76, "shell.ts, ui.ts", "DOM layer: sections, panels, rail, phone stops"))
    out.append(node(t, 260, y + 150, 220, 76, "director.ts", "renderer, camera, layout, flights", accent=True))
    out.append(node(t, 40, y + 248, 150, 52, "content/resume.ts", "all resume text"))
    out.append(node(t, 260, y + 248, 220, 52, "resume.html", "static, printable page"))
    out += [line(t, 190, y + 120, 260, y + 38), line(t, 190, y + 120, 260, y + 188),
            text(t, "WebGL2", MONO, 10, 238, y + 150, color=t["accent"], anchor="end")[0],
            line(t, 370, y + 150, 370, y + 76), text(t, "hooks", MONO, 10, 380, y + 118, color=t["accent"])[0],
            line(t, 190, y + 274, 260, y + 274)]
    for i, (name, sub) in enumerate((("worlds/*", "ray-traced planet shaders"), ("sky.ts", "stars, Milky Way, constellations"),
                                     ("events.ts", "sky event scheduler"), ("flare.ts", "Sun and lens flare"),
                                     ("music.ts", "Web Audio, off by default"))):
        ny = y + i * 62
        out.append(node(t, 560, ny, 280, 52, name, sub, dim=True))
        out.append(f'<path d="M480 {y + 188}L560 {ny + 26}" stroke="{t["ink"]}" stroke-opacity=".18"/>')
    return "".join(out)


def g_perf(t):
    h, y = head(t, "PERFORMANCE", "Resolution and textures follow the device.")
    out = [frame(t, 470), h]
    out.append(kicker(t, "FRAME-TIME GOVERNOR  ·  RENDER SCALE", 40, y, accent=True))
    out.append(bars(t, [(f"step {i}", v, i == 0) for i, v in enumerate((100, 85, 70, 60, 50))], 40, y + 40, 300, row=44))
    out.append(lines(t, "Average over 22 ms for about 2 s: one step down.\nUnder 12 ms for about 8 s: one step back up.",
                     SANS, 13, 40, y + 266, 380, 19, op=.85)[0])
    out.append(kicker(t, "TEXTURE TIERS", 470, y, accent=True))
    for i, (tier, note) in enumerate((("low", "touch screens or 4 GB of memory or less"),
                                      ("mid", "the default on other devices"),
                                      ("high", "only the world you've flown to"))):
        ty = y + 24 + i * 62
        out.append(box(t, 470, ty, 370, 50, accent=i == 2))
        out.append(text(t, tier, JOST_MED, 15, 486, ty + 31)[0])
        out.append(text(t, note, SANS, 12.5, 540, ty + 31, op=.85)[0])
    out.append(lines(t, "Maps decode off the main thread with createImageBitmap and upload one per frame.",
                     SANS, 13, 470, y + 230, 370, 19, op=t["dim"])[0])
    return "".join(out)


GRAPHICS = {
    "hero": (400, g_hero, "Personal website: a resume as a real-time 3D solar system with 6 worlds. Earth holds About, the Moon Education, Jupiter Experience, Mars Projects, Saturn Skills and Neptune Contact"),
    "architecture": (470, g_arch, "Architecture: main.ts starts the DOM layer, and with WebGL2 loads director.ts, which drives the worlds, sky, events, flare and music and fills hooks in the DOM layer. content/resume.ts feeds the site and resume.html"),
    "performance": (470, g_perf, "Performance: a frame-time governor steps render scale from 100% down to 50% when frames average over 22 ms, and back up under 12 ms; textures load in low, mid and high tiers"),
}
