"""README graphics for haashirk20/customertransactionanalysis. Colours follow the notebook's seaborn
palettes, Blues_r for spending and Reds_r for fraud. Counts are the notebook's printed outputs."""
import math

from kit import W, box, cells, frame, head, hero, kicker, lines, steps, text
from build import JOST, JOST_MED, MONO, SANS

THEMES = {
    "dark": {"bg": "#08306B", "ink": "#F7FBFF", "dim": 0.72, "line": 0.2, "accent": "#FC9272", "panel": "#2171B5"},
    "light": {"bg": "#F7FBFF", "ink": "#08306B", "dim": 0.68, "line": 0.15, "accent": "#CB181D", "panel": "#DEEBF7"},
}


def bell(t, x, y, w, h, label=True):
    """A normal curve with everything past mean + 3 sigma shaded as flagged. A concept sketch, not data."""
    pts, tail = [], []
    for i in range(121):
        z = -4 + 8 * i / 120
        px, py = x + w * i / 120, y + h - h * math.exp(-z * z / 2)
        pts.append(f"{px:.1f},{py:.1f}")
        if z >= 3:
            tail.append(f"{px:.1f},{py:.1f}")
    x3 = x + w * 7 / 8
    out = [f'<polyline points="{" ".join(pts)}" fill="none" stroke="{t["ink"]}" stroke-opacity=".8" stroke-width="1.6"/>',
           f'<rect x="{x3:.1f}" y="{y}" width="{x + w - x3:.1f}" height="{h}" fill="{t["accent"]}" fill-opacity=".18"/>',
           f'<polygon points="{x3:.1f},{y + h} {" ".join(tail)} {x + w},{y + h}" fill="{t["accent"]}" fill-opacity=".85"/>',
           f'<path d="M{x3:.1f} {y - 6}V{y + h}" stroke="{t["accent"]}" stroke-dasharray="4 3"/>',
           f'<path d="M{x + w / 2} {y}V{y + h}" stroke="{t["ink"]}" stroke-opacity=".3" stroke-dasharray="2 3"/>',
           f'<rect x="{x}" y="{y + h}" width="{w}" height="1" fill="{t["ink"]}" fill-opacity=".35"/>']
    if label:
        out.append(text(t, "customer's mean", MONO, 10.5, x + w / 2, y + h + 18, op=t["dim"], anchor="middle")[0])
        out.append(text(t, "mean + 3 SD", MONO, 10.5, x3, y - 12, color=t["accent"], anchor="middle")[0])
    return "".join(out)


def g_hero(t):
    return hero(t, "DATA ANALYSIS  ·  PYTHON + POWER BI  ·  2025", "Customer\nTransactions",
                "Exploratory analysis of card transactions, with two rule-based checks that flag possible fraud.",
                [("13.3M", "transactions"), ("2,612", "travel flags"), ("203", "spending flags")],
                "Flag counts are on a 20,000-row sample.",
                figure=lambda t: (f'<rect x="520" y="60" width="320" height="280" rx="10" fill="{t["panel"]}" fill-opacity=".55"/>'
                                  + text(t, "SPENDING CHECK", JOST, 10.5, 544, 92, op=.8, tracking=0.24)[0]
                                  + bell(t, 548, 140, 264, 140)))


def g_pipeline(t):
    h, y = head(t, "PIPELINE", "From 13.3 million rows to two lists of flags.")
    return frame(t, 300) + h + steps(t, [
        ("Kaggle data", "13,305,915 transactions"),
        ("Join MCC codes", "merchant categories from mcc_codes.json"),
        ("Clean", "parse amounts, N/A for online, time parts"),
        ("Explore", "charts on a 20,000-row sample"),
        ("Flag", "impossible travel and 3 SD spending"),
    ], 40, y, W - 80, h=112, accent=4)


def g_checks(t):
    h, y = head(t, "FRAUD CHECKS", "Two rules, both vectorised with no row loops.")
    out = [frame(t, 470), h]
    # Impossible travel: two transactions by one card, different cities, under two hours apart.
    out.append(kicker(t, "IMPOSSIBLE TRAVEL", 40, y, accent=True))
    ty = y + 80
    out.append(f'<rect x="40" y="{ty}" width="380" height="1" fill="{t["ink"]}" fill-opacity=".4"/>')
    for px, city, when in ((80, "City A", "previous transaction"), (300, "City B", "same card, < 2 hours later")):
        out.append(f'<circle cx="{px}" cy="{ty}" r="7" fill="{t["accent"] if px > 100 else t["ink"]}"/>')
        out.append(text(t, city, JOST_MED, 15, px, ty - 18, anchor="middle")[0])
        out.append(text(t, when, MONO, 10.5, px, ty + 26, op=t["dim"], anchor="middle")[0])
    out.append(lines(t, "Sorted by customer and time, then groupby().diff() and shift() compare each row with the same card's previous one.",
                     SANS, 13, 40, ty + 64, 380, 19, op=.85)[0])
    # Spending anomaly.
    out.append(kicker(t, "SPENDING ANOMALY", 460, y, accent=True))
    out.append(bell(t, 470, y + 34, 360, 68))
    out.append(lines(t, "Each customer's mean and standard deviation are merged back, so a big spender isn't flagged for a normal purchase.",
                     SANS, 13, 460, ty + 64, 380, 19, op=.85)[0])
    out.append(cells(t, [("2,612", "FLAGGED: TRAVEL", True), ("203", "FLAGGED: SPENDING", True)], 40, ty + 116, 395, 84, cols=2, gap=10))
    out.append(text(t, "On the first 20,000 cleaned rows. Not scored against labelled fraud, so precision is unknown.", MONO, 11, 40, ty + 226, op=t["dim"])[0])
    return "".join(out)


GRAPHICS = {
    "hero": (400, g_hero, "Customer transaction analysis: 13.3 million transactions; on a 20,000-row sample, 2,612 impossible-travel flags and 203 spending flags"),
    "pipeline": (300, g_pipeline, "Pipeline: Kaggle data, join merchant category codes, clean, explore on a 20,000-row sample, flag"),
    "fraud-checks": (470, g_checks, "Fraud checks: impossible travel, a card used in a different city within two hours; spending anomaly, above the customer's mean plus three standard deviations. 2,612 and 203 flags"),
}
