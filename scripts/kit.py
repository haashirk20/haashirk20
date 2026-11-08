"""Graphics kit for project READMEs.

Each README graphic is one 880px-wide card: a kicker, a headline, and a figure built from
the primitives below (steps, bars, cells, rows, tiles, chip lists, a hero).
A spec file per repository composes them and sets THEMES from that project's own colours;
see scripts/specs/. Theme keys: bg, ink, dim, line, accent, panel.

    python scripts/kit.py scripts/specs/<repo>.py <repo checkout>
"""
import importlib.util
import sys
from pathlib import Path

from build import JOST, JOST_MED, MONO, SANS, chips, num, svg, text_path, wrap

W = 880


def text(t, s, font, size, x, y, op=1.0, color=None, tracking=0.0, anchor="start"):
    d, w = text_path(s, font, size, x, y, tracking=tracking, anchor=anchor)
    return f'<path d="{d}" fill="{color or t["ink"]}" fill-opacity="{op}"/>', w


def lines(t, s, font, size, x, y, maxw, lead, op=1.0, color=None):
    """Wrapped text; also honours explicit newlines. Returns (svg, y of the last baseline)."""
    out, row = [], 0
    for para in s.split("\n"):
        for ln in wrap(para, font, size, maxw):
            out.append(text_path(ln, font, size, x, y + row * lead)[0])
            row += 1
    return f'<path d="{"".join(out)}" fill="{color or t["ink"]}" fill-opacity="{op}"/>', y + (row - 1) * lead


def frame(t, h, w=W):
    return f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="4" fill="{t["bg"]}" stroke="{t["ink"]}" stroke-opacity="{t["line"]}"/>'


def kicker(t, s, x, y, accent=False):
    return text(t, s, JOST, 11.5, x, y, op=1 if accent else t["dim"], color=t["accent"] if accent else None, tracking=0.3)[0]


def head(t, k, title, x=40, y=52, maxw=800):
    """Kicker plus headline. Returns (svg, y where content can start)."""
    s = kicker(t, k, x, y)
    h, last = lines(t, title, JOST_MED, 29, x, y + 42, maxw, 36)
    return s + h, last + 40


def box(t, x, y, w, h, accent=False, op=None):
    stroke = t["accent"] if accent else t["ink"]
    return f'<rect x="{num(x + .5)}" y="{num(y + .5)}" width="{num(w - 1)}" height="{num(h - 1)}" rx="3" fill="none" stroke="{stroke}" stroke-opacity="{op if op is not None else (.9 if accent else .22)}"/>'


def fillrect(t, x, y, w, h, op, accent=False):
    return f'<rect x="{num(x)}" y="{num(y)}" width="{num(w)}" height="{num(h)}" rx="2" fill="{t["accent"] if accent else t["ink"]}" fill-opacity="{op}"/>'


def steps(t, items, x, y, w, h=104, gap=24, accent=None):
    """A left-to-right pipeline of boxes: (title, detail) pairs, joined by short connectors."""
    n = len(items)
    bw = (w - gap * (n - 1)) / n
    out = []
    for i, (title, detail) in enumerate(items):
        bx = x + i * (bw + gap)
        out.append(box(t, bx, y, bw, h, accent=(i == accent)))
        out.append(text(t, f"{i + 1:02d}", MONO, 11, bx + 14, y + 22, color=t["accent"])[0])
        tp, ty = lines(t, title, JOST_MED, 15.5, bx + 14, y + 44, bw - 26, 19)
        out.append(tp)
        out.append(lines(t, detail, MONO, 10.5, bx + 14, ty + 20, bw - 24, 15, op=t["dim"] + .1)[0])
        if i < n - 1:
            out.append(f'<path d="M{num(bx + bw + 4)} {y + h / 2}h{gap - 8}" stroke="{t["ink"]}" stroke-opacity=".45"/>'
                       f'<path d="M{num(bx + bw + gap - 8)} {y + h / 2 - 3}l4 3-4 3" fill="none" stroke="{t["ink"]}" stroke-opacity=".45"/>')
    return "".join(out)


def bars(t, items, x, y, w, maxv=100, fmt="{:g}%", row=58):
    """Horizontal bars with direct labels: (label, value, highlight)."""
    out = []
    for i, (label, v, hi) in enumerate(items):
        ry = y + i * row
        out.append(text(t, label, SANS, 13.5, x, ry, op=.88)[0])
        out.append(fillrect(t, x, ry + 12, w, 10, .08))
        bw = w * v / maxv
        out.append(fillrect(t, x, ry + 12, bw, 10, 1 if hi else .35, accent=hi))
        out.append(text(t, fmt.format(v), JOST_MED, 16, x + bw + 10, ry + 22)[0])
    return "".join(out)


def cells(t, items, x, y, cw, ch, cols=2, gap=6):
    """Value tiles in a grid: (value, label, emphasis). Values are printed, shading is secondary."""
    out = []
    for i, (v, label, emph) in enumerate(items):
        cx, cy = x + (i % cols) * (cw + gap), y + (i // cols) * (ch + gap)
        out.append(fillrect(t, cx, cy, cw, ch, .14 if emph else .05, accent=emph))
        out.append(box(t, cx, cy, cw, ch, accent=emph, op=.6 if emph else .2))
        out.append(text(t, v, JOST_MED, 30, cx + 14, cy + 42)[0])
        out.append(text(t, label, JOST, 10, cx + 14, cy + ch - 16, op=.7, tracking=0.2)[0])
    return "".join(out)


def rows(t, items, x, y, w, row=46):
    """A numbered list with hairlines, like a ladder: (title, note, highlight)."""
    out = [fillrect(t, x, y, w, 1, t["line"])]
    for i, (title, note, hi) in enumerate(items):
        ry = y + i * row
        out.append(text(t, str(i + 1), MONO, 13, x, ry + 29, color=t["accent"] if hi else None, op=1 if hi else t["dim"])[0])
        out.append(text(t, title, JOST_MED if hi else SANS, 15.5, x + 40, ry + 29)[0])
        if note:
            out.append(text(t, note, MONO, 11.5, x + w, ry + 29, op=t["dim"], anchor="end")[0])
        out.append(fillrect(t, x, ry + row, w, 1, t["line"]))
    return "".join(out)


def tiles(t, items, x, y, w, cols=2, gap=16, h=None):
    """Feature tiles: (title, body). Height fits the longest body unless h is given."""
    tw = (w - gap * (cols - 1)) / cols
    rendered = []
    for title, body in items:
        tp, _ = text(t, title, JOST_MED, 16, 0, 0)
        bp, last = lines(t, body, SANS, 13.5, 0, 0, tw - 36, 20, op=.8)
        rendered.append((title, body, last))
    th = h or max(r[2] for r in rendered) + 74
    out = []
    for i, (title, body, _) in enumerate(rendered):
        tx, ty = x + (i % cols) * (tw + gap), y + (i // cols) * (th + gap)
        out.append(box(t, tx, ty, tw, th))
        out.append(text(t, title, JOST_MED, 16, tx + 18, ty + 32)[0])
        out.append(lines(t, body, SANS, 13.5, tx + 18, ty + 56, tw - 36, 20, op=.8)[0])
    nrows = (len(items) + cols - 1) // cols
    return "".join(out), y + nrows * th + (nrows - 1) * gap


def chiplist(t, label, items, x, y, w, accent=False):
    """A labelled group of outlined chips. Returns (svg, bottom y)."""
    k = kicker(t, label, x, y, accent=accent)
    c, bottom = chips(t, items, x, y + 14, w)
    return k + c, bottom


def boxes(t, items, x, y, w, dim=False, row=32):
    """Stacked outlined labels; dim ones read as excluded."""
    out = []
    for i, s in enumerate(items):
        out.append(box(t, x, y + i * row, w, row - 6, op=.12 if dim else .26))
        out.append(text(t, s, MONO, 12, x + 12, y + i * row + 17, op=.45 if dim else .92)[0])
    return "".join(out)


def hero(t, k, title, pitch, stats, foot, figure=None, h=400):
    """Title card: name, pitch and headline numbers on the left; a project figure (a callable
    drawing into x 500..840) on the right."""
    out = [frame(t, h), kicker(t, k, 40, 52)]
    tp, ty = lines(t, title, JOST_MED, 48, 40, 108, 440, 54)
    out.append(tp)
    pp, py = lines(t, pitch, SANS, 16, 40, ty + 40, 420, 23, op=.88)
    out.append(pp)
    sy = py + 58
    # Columns are at least a quarter of the 430px band, wider when a value or label needs it.
    sx = 40
    for v, label in stats:
        vp, vw = text(t, v, JOST_MED, 30, sx, sy)
        lp, lw = text(t, label.upper(), JOST, 10, sx, sy + 22, op=t["dim"], tracking=0.22)
        out += [vp, lp]
        sx += max(430 / max(len(stats), 1), vw + 28, lw + 28)
    out.append(fillrect(t, 40, h - 52, 420, 1, t["line"]))
    out.append(text(t, foot, MONO, 11, 40, h - 28, op=t["dim"])[0])
    if figure:
        out.append(figure(t))
    return "".join(out)


def build(spec_path, repo):
    spec = importlib.util.spec_from_file_location("spec", spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    out = Path(repo) / "assets" / "readme"
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for name, (h, fn, title) in mod.GRAPHICS.items():
        for theme, t in mod.THEMES.items():
            p = out / f"{name}-{theme}.svg"
            p.write_text(svg(W, h, fn(t), "", title), encoding="utf-8")
            total += p.stat().st_size
    print(f"{out}: {len(mod.GRAPHICS)} graphics, {total / 1024:.0f} KB")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
