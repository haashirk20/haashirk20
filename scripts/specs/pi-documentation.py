"""README graphics for haashirk20/pi-documentation. Colours come from template.mustache, the page the tool
generates: Bootstrap greys #343A40, #495057, #F8F9FA and #E9ECEF, blue #007BFF, teal #17A2B8, green #28A745."""
from kit import W, box, fillrect, frame, head, hero, kicker, lines, steps, text
from build import JOST, JOST_MED, MONO, SANS

THEMES = {
    "dark": {"bg": "#343A40", "ink": "#F8F9FA", "dim": 0.72, "line": 0.2, "accent": "#17A2B8", "panel": "#495057"},
    "light": {"bg": "#F8F9FA", "ink": "#343A40", "dim": 0.68, "line": 0.15, "accent": "#007BFF", "panel": "#E9ECEF"},
}


def page(t):
    """The generated page: one collapsible bar per service, the open one showing its info and flows tables.
    Drawn in the template's own light colours in both themes, since that is how the page looks."""
    x, y, w, h = 520, 36, 320, 330
    ink = "#333333"
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#FFFFFF" stroke="{t["ink"]}" stroke-opacity=".2"/>',
           text(t, "<username>", JOST_MED, 17, x + 16, y + 32, color=ink)[0],
           text(t, "EXAMPLE OUTPUT", JOST, 9.5, x + w - 16, y + 30, color=ink, op=.6, tracking=0.24, anchor="end")[0]]
    by = y + 46
    # Open service: green bar, info table, flows table.
    out.append(f'<rect x="{x + 12}" y="{by}" width="{w - 24}" height="26" rx="3" fill="#28A745"/>')
    out.append(text(t, "flows-dev: 1880", JOST_MED, 12, x + 22, by + 17, color="#FFFFFF")[0])
    ty = by + 34
    for i, (k, v) in enumerate((("IP Address", "localhost"), ("Port", "1880"), ("Node-RED Version", "x.y.z"))):
        ry = ty + i * 20
        out.append(f'<rect x="{x + 22}" y="{ry}" width="110" height="20" fill="#F4F4F4" stroke="#CCCCCC"/>')
        out.append(f'<rect x="{x + 132}" y="{ry}" width="90" height="20" fill="#FFFFFF" stroke="#CCCCCC"/>')
        out.append(text(t, k, SANS, 9.5, x + 28, ry + 14, color=ink)[0])
        out.append(text(t, v, SANS, 9.5, x + 138, ry + 14, color=ink)[0])
    fy = ty + 72
    cols = [(x + 22, "Type"), (x + 72, "Label"), (x + 142, "Status"), (x + 196, "Description")]
    rows_ = [("Type", "Label", "Status", "Description"), ("tab", "Orders", "Enabled", "Polls the order API"),
             ("tab", "Alerts", "Disabled", "Flow Disabled; See..."), ("subflow", "Retry", "Enabled", "")]
    for r, row in enumerate(rows_):
        ry = fy + r * 20
        out.append(f'<rect x="{x + 22}" y="{ry}" width="{w - 44}" height="20" fill="{"#F4F4F4" if r == 0 else "#FFFFFF"}" stroke="#CCCCCC"/>')
        for (cx, _), cell in zip(cols, row):
            out.append(text(t, cell, JOST_MED if r == 0 else SANS, 9.5, cx + 6, ry + 14, color=ink)[0])
    # Closed services.
    for i, name in enumerate(("flows-api: 1881", "flows-etl: 1882")):
        sy = fy + 94 + i * 32
        out.append(f'<rect x="{x + 12}" y="{sy}" width="{w - 24}" height="26" rx="3" fill="#343A40"/>')
        out.append(text(t, name, JOST_MED, 12, x + 22, sy + 17, color="#FFFFFF")[0])
    return "".join(out)


def g_hero(t):
    return hero(t, "COMMAND-LINE TOOL  ·  NODE-RED", "pi-documentation",
                "One HTML page per user that documents every Node-RED service running under PM2.",
                [("3", "API calls per service"), ("1", "page per user"), ("3", "environments")],
                "Node.js · axios · Mustache · Bash", figure=page)


def g_pipeline(t):
    h, y = head(t, "HOW IT WORKS", "Gather to JSON, then render the JSON to HTML.")
    return (frame(t, 320) + h + steps(t, [
        ("ecosystem.config.js", "PM2 apps with IP, PORT and TOKEN in env"),
        ("gatherServiceData", "GET /flows, /settings, /diagnostics"),
        ("serviceData.json", "raw data, kept on disk"),
        ("renderTemplate", "fills template.mustache, writes <username>.html"),
    ], 40, y, W - 80, h=112, accent=1)
        + text(t, "A service with no port or token is skipped. One that fails is logged and left off the page.", SANS, 13, 40, y + 148, op=t["dim"])[0])


def g_modes(t):
    h, y = head(t, "TWO MODES", "document.sh runs one user, or dev, test and prod.")
    out = [frame(t, 400), h]
    cw = (W - 80 - 24) / 2
    for i, (title, cmd, items, hi) in enumerate((
            ("LOCAL", "./document.sh local <username> <ecosystem>", [("<username>", "<username>.html")], False),
            ("FULL", "./document.sh full <dev> <test> <prod>",
             [("sudo -u nodereddev", "nodereddev.html"), ("sudo -u noderedtest", "noderedtest.html"),
              ("sudo -u noderedprod", "noderedprod.html")], True))):
        cx = 40 + i * (cw + 24)
        out.append(kicker(t, title, cx, y, accent=hi))
        out.append(text(t, cmd, MONO, 11.5, cx, y + 24, op=.92)[0])
        for j, (who, out_file) in enumerate(items):
            ry = y + 44 + j * 44
            out.append(box(t, cx, ry, cw, 36, accent=hi and j == 0, op=None if hi and j == 0 else .25))
            out.append(text(t, who, MONO, 11.5, cx + 14, ry + 23)[0])
            out.append(text(t, out_file, MONO, 11.5, cx + cw - 14, ry + 23, op=t["dim"], anchor="end")[0])
    out.append(lines(t, "Full mode runs node once per environment as that environment's system user, each with its own ecosystem file, so every environment gets its own page.",
                     SANS, 13, 40, y + 210, W - 80, 19, op=t["dim"])[0])
    return "".join(out)


GRAPHICS = {
    "hero": (400, g_hero, "pi-documentation: a command-line tool that writes one HTML page per user documenting every Node-RED service under PM2, with 3 API calls per service and 3 environments in full mode. Example of the generated page"),
    "how-it-works": (320, g_pipeline, "How it works: ecosystem.config.js, gatherServiceData calls /flows, /settings and /diagnostics, serviceData.json, renderTemplate fills template.mustache and writes username.html"),
    "modes": (400, g_modes, "Two modes: local documents one user; full runs as nodereddev, noderedtest and noderedprod and writes a page for each"),
}
