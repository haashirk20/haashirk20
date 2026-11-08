"""README graphics for haashirk20/py-stock-predictor. The app has no theme of its own, so the colours are
Streamlit's defaults: primary #FF4B4B, dark background #0E1117 with #262730 surfaces, light #FFFFFF with #F0F2F6."""
import math
import random

from kit import W, box, frame, head, hero, kicker, lines, steps, text
from build import JOST, JOST_MED, MONO, SANS

THEMES = {
    "dark": {"bg": "#0E1117", "ink": "#FAFAFA", "dim": 0.66, "line": 0.18, "accent": "#FF4B4B", "panel": "#262730"},
    "light": {"bg": "#FFFFFF", "ink": "#31333F", "dim": 0.66, "line": 0.14, "accent": "#FF4B4B", "panel": "#F0F2F6"},
}


def forecast(t):
    """An illustration of the app's forecast chart: price history, then the forecast line and its band."""
    x, y, w, h = 520, 70, 320, 230
    rng = random.Random(3)
    hist, v = [], 60.0
    for i in range(70):
        v += rng.gauss(0.35, 2.2)
        hist.append(v)
    split = x + w * .62
    pts = [(x + (split - x) * i / 69, y + h - 30 - (p - 40) * 1.4) for i, p in enumerate(hist)]
    lx, ly = pts[-1]
    up, mid, lo = [], [], []
    for i in range(31):
        px = split + (x + w - split) * i / 30
        my = ly - i * 1.6
        spread = 4 + i * 1.3
        mid.append(f"{px:.1f},{my:.1f}")
        up.append(f"{px:.1f},{my - spread:.1f}")
        lo.append(f"{px:.1f},{my + spread:.1f}")
    band = " ".join(up) + " " + " ".join(reversed(lo))
    return (f'<rect x="{x - 20}" y="{y - 30}" width="{w + 40}" height="{h + 70}" rx="10" fill="{t["panel"]}"/>'
            + text(t, "FORECAST  ·  ILLUSTRATION", JOST, 10, x, y - 6, op=.75, tracking=0.24)[0]
            + f'<path d="M{split:.1f} {y}V{y + h}" stroke="{t["ink"]}" stroke-opacity=".3" stroke-dasharray="3 4"/>'
            + f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{t["ink"]}" stroke-opacity=".85" stroke-width="1.5"/>'
            + f'<polygon points="{band}" fill="{t["accent"]}" fill-opacity=".18"/>'
            + f'<polyline points="{" ".join(mid)}" fill="none" stroke="{t["accent"]}" stroke-width="2"/>'
            + text(t, "history since 2015", MONO, 10.5, x, y + h + 24, op=t["dim"])[0]
            + text(t, "1 to 4 years ahead", MONO, 10.5, x + w, y + h + 24, op=t["dim"], anchor="end")[0])


def g_hero(t):
    return hero(t, "STREAMLIT APP  ·  TIME SERIES  ·  2023", "Stock Predictor",
                "Type a ticker, pick 1 to 4 years, and get a Prophet forecast of the closing price.",
                [("2015", "data from"), ("1 to 4", "years ahead"), ("3", "charts")],
                "A proof of concept. Not for financial decisions.", figure=forecast)


def g_flow(t):
    h, y = head(t, "HOW IT WORKS", "One slider controls the whole forecast window.")
    return frame(t, 300) + h + steps(t, [
        ("Ticker + years", "text box and a 1 to 4 slider"),
        ("load_data", "yf.download since 2015, st.cache_data"),
        ("Prepare", "Date, Close renamed to ds, y"),
        ("Prophet().fit", "trend plus weekly and yearly seasonality"),
        ("Forecast", "years x 365 days, chart and components"),
    ], 40, y, W - 80, accent=3)


def code(t, x, y, w, title, lines_, ok):
    out = [box(t, x, y, w, 40 + 22 * len(lines_), accent=ok, op=.8 if ok else .3),
           kicker(t, title, x + 16, y + 24, accent=ok)]
    for i, (ln, hi) in enumerate(lines_):
        out.append(text(t, ln, MONO, 12, x + 16, y + 52 + i * 22, color=t["accent"] if hi else None, op=1 if hi else .85)[0])
    return "".join(out)


def g_fix(t):
    h, y = head(t, "KNOWN ISSUE", "One argument makes it work with current yfinance.")
    return (frame(t, 360) + h
            + code(t, 40, y, 390, "AS WRITTEN", [("data = yf.download(ticker, START, TODAY)", False),
                                                 ("# columns: ('Close', 'AAPL'), ...", False),
                                                 ("m.fit(df_train)", False),
                                                 ("TypeError: arg must be a list, ...", True)], False)
            + code(t, 450, y, 390, "WITH THE FIX", [("data = yf.download(ticker, START, TODAY,", False),
                                                    ("    multi_level_index=False)", True),
                                                    ("# columns: 'Close', 'Open', ...", False),
                                                    ("m.fit(df_train)  # fits normally", False)], True)
            + text(t, "Tested with yfinance 1.8.0 and Prophet 1.5.0.", MONO, 11, 40, y + 160, op=t["dim"])[0])


GRAPHICS = {
    "hero": (400, g_hero, "Stock Predictor: a Streamlit app that forecasts a stock's closing price 1 to 4 years ahead with Prophet, from data since 2015. Illustrated forecast chart"),
    "how-it-works": (300, g_flow, "How it works: ticker and years, load_data with yfinance since 2015, rename to ds and y, fit Prophet, forecast years times 365 days"),
    "known-issue": (360, g_fix, "Known issue: current yfinance returns two-level columns and Prophet's fit raises a TypeError; passing multi_level_index=False fixes it"),
}
