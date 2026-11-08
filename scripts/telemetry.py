"""Renders the telemetry card from the GitHub GraphQL API, in the same style as the other assets.

Runs daily in .github/workflows/profile.yml. Needs GITHUB_TOKEN in the environment.

    python scripts/telemetry.py <login> <out_dir>
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from collections import Counter
from pathlib import Path

from build import JOST, JOST_MED, MONO, THEMES, num, svg, text_path


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

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } }
    }
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}
"""
# Markup, typesetting and build files would swamp the byte counts, so they are left out.
SKIP = {"HTML", "CSS", "SCSS", "TeX", "CMake", "Makefile", "Dockerfile", "Batchfile", "Procfile"}
SHORT = {"Jupyter Notebook": "Jupyter"}


def fetch(login, token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def summarize(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    # The current streak may end yesterday: today isn't over yet.
    current, tail = 0, counts[:-1] if counts and counts[-1] == 0 else counts
    for c in reversed(tail):
        if not c:
            break
        current += 1
    langs = Counter()
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            if e["node"]["name"] not in SKIP:
                langs[e["node"]["name"]] += e["size"]
    total = sum(langs.values()) or 1
    top = [(SHORT.get(k, k), v / total) for k, v in langs.most_common(5)]
    weekly = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
    return {
        "contributions": cal["totalContributions"], "current": current, "longest": longest,
        "repos": user["repositories"]["totalCount"], "langs": top, "weekly": weekly,
        "updated": dt.date.today().isoformat(),
    }


def telemetry(t, s):
    w, h = 560, 400
    ink = t["ink"]
    parts = [card(t, w, h, "04", "TELEMETRY")]
    up, _ = text_path(f"UPDATED {s['updated']}", MONO, 10.5, 532, 48, anchor="end")
    parts.append(f'<path d="{up}" fill="{ink}" fill-opacity="{t["dim"]}"/>')
    readouts = [
        (f"{s['contributions']:,}", "", "CONTRIBUTIONS, PAST YEAR"),
        (str(s["repos"]), "", "PUBLIC REPOSITORIES"),
        (str(s["current"]), "DAYS" if s["current"] != 1 else "DAY", "CURRENT STREAK"),
        (str(s["longest"]), "DAYS" if s["longest"] != 1 else "DAY", "LONGEST STREAK, PAST YEAR"),
    ]
    for i, (value, unit, label) in enumerate(readouts):
        x, y = 116 + (i % 2) * 216, 118 + (i // 2) * 76
        v, vw = text_path(value, JOST_MED, 36, x, y)
        lab, _ = text_path(label, JOST, 10.5, x, y + 22, tracking=0.26)
        parts.append(f'<path d="{v}" fill="{ink}"/><path d="{lab}" fill="{ink}" fill-opacity="{t["dim"]}"/>')
        if unit:
            u, _ = text_path(unit, JOST, 12, x + vw + 8, y, tracking=0.2)
            parts.append(f'<path d="{u}" fill="{t["accent"]}"/>')
    # Weekly contributions as a thin trace.
    weekly = s["weekly"]
    x0, x1, base, height = 116, 532, 296, 40
    peak = max(weekly) or 1
    pts = [(x0 + (x1 - x0) * i / max(len(weekly) - 1, 1), base - height * c / peak) for i, c in enumerate(weekly)]
    line = " ".join(f"{num(x)},{num(y)}" for x, y in pts)
    lab, _ = text_path("WEEKLY CONTRIBUTIONS", JOST, 10.5, x0, base - height - 10, tracking=0.26)
    parts.append(
        f'<path d="{lab}" fill="{ink}" fill-opacity="{t["dim"]}"/>'
        f'<rect x="{x0}" y="{base}" width="{x1 - x0}" height="1" fill="{ink}" fill-opacity="{t["line"]}"/>'
        f'<polygon points="{x0},{base} {line} {x1},{base}" fill="{t["accent"]}" fill-opacity=".12"/>'
        f'<polyline points="{line}" fill="none" stroke="{t["accent"]}" stroke-width="1.2" stroke-linejoin="round"/>'
    )
    # Language mix: one bar in steps of grey, with a legend underneath.
    by, x = 330, float(x0)
    shades = [1, 0.72, 0.5, 0.34, 0.22]
    lx, ly = float(x0), by + 30
    for (name, frac), op in zip(s["langs"], shades):
        seg = (x1 - x0) * frac
        parts.append(f'<rect x="{num(x)}" y="{by}" width="{num(max(seg - 2, 1))}" height="5" fill="{ink}" fill-opacity="{op}"/>')
        x += seg
        item, iw = text_path(f"{name.upper()} {frac * 100:.0f}%", JOST, 10.5, lx + 12, ly, tracking=0.2)
        if lx + 12 + iw > x1:
            lx, ly = float(x0), ly + 22
            item, iw = text_path(f"{name.upper()} {frac * 100:.0f}%", JOST, 10.5, lx + 12, ly, tracking=0.2)
        parts.append(f'<rect x="{num(lx)}" y="{ly - 7}" width="7" height="7" fill="{ink}" fill-opacity="{op}"/><path d="{item}" fill="{ink}" fill-opacity=".85"/>')
        lx += 12 + iw + 22
    title = f"Telemetry: {s['contributions']} contributions in the past year, {s['repos']} public repositories"
    return svg(w, h, "".join(parts), "", title)


if __name__ == "__main__":
    login, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    stats = summarize(fetch(login, os.environ["GITHUB_TOKEN"]))
    for theme, t in THEMES.items():
        (out / f"telemetry-{theme}.svg").write_text(telemetry(t, stats), encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "weekly"}))
