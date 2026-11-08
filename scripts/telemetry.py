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

from build import JOST, JOST_MED, MONO, THEMES, W, num, svg, text_path


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
    """One wide card in three zones: readouts, weekly trace, language mix."""
    w, h = W, 236
    ink, line = t["ink"], t["line"]
    parts = [card(t, w, h, "04", "TELEMETRY")]
    up, _ = text_path(f"UPDATED {s['updated']}", MONO, 10.5, w - 24, 48, anchor="end")
    parts.append(f'<path d="{up}" fill="{ink}" fill-opacity="{t["dim"]}"/>')
    for x in (494, 700):
        parts.append(f'<rect x="{x}" y="80" width="1" height="132" fill="{ink}" fill-opacity="{line}"/>')

    # Zone 1: four readouts in a 2x2 grid.
    readouts = [
        (f"{s['contributions']:,}", "", "CONTRIBUTIONS, 12 MO"),
        (str(s["repos"]), "", "PUBLIC REPOSITORIES"),
        (str(s["current"]), "DAYS" if s["current"] != 1 else "DAY", "CURRENT STREAK"),
        (str(s["longest"]), "DAYS" if s["longest"] != 1 else "DAY", "LONGEST STREAK, 12 MO"),
    ]
    for i, (value, unit, label) in enumerate(readouts):
        x, y = 92 + (i % 2) * 200, 120 + (i // 2) * 74
        v, vw = text_path(value, JOST_MED, 34, x, y)
        lab, _ = text_path(label, JOST, 10.5, x, y + 21, tracking=0.2)
        parts.append(f'<path d="{v}" fill="{ink}"/><path d="{lab}" fill="{ink}" fill-opacity="{t["dim"]}"/>')
        if unit:
            u, _ = text_path(unit, JOST, 11.5, x + vw + 8, y, tracking=0.2)
            parts.append(f'<path d="{u}" fill="{t["accent"]}"/>')

    # Zone 2: weekly contributions as a thin trace.
    weekly = s["weekly"]
    x0, x1, base, height = 518, 676, 196, 70
    peak = max(weekly) or 1
    pts = [(x0 + (x1 - x0) * i / max(len(weekly) - 1, 1), base - height * c / peak) for i, c in enumerate(weekly)]
    trace = " ".join(f"{num(x)},{num(y)}" for x, y in pts)
    lab, _ = text_path("WEEKLY CONTRIBUTIONS", JOST, 10.5, x0, 98, tracking=0.2)
    parts.append(
        f'<path d="{lab}" fill="{ink}" fill-opacity="{t["dim"]}"/>'
        f'<rect x="{x0}" y="{base}" width="{x1 - x0}" height="1" fill="{ink}" fill-opacity="{line}"/>'
        f'<polygon points="{x0},{base} {trace} {x1},{base}" fill="{t["accent"]}" fill-opacity=".12"/>'
        f'<polyline points="{trace}" fill="none" stroke="{t["accent"]}" stroke-width="1.2" stroke-linejoin="round"/>'
    )

    # Zone 3: language mix as labelled rows, so colour is never the only cue.
    lx, rx = 724, w - 24
    lab, _ = text_path("LANGUAGES", JOST, 10.5, lx, 98, tracking=0.2)
    parts.append(f'<path d="{lab}" fill="{ink}" fill-opacity="{t["dim"]}"/>')
    top = s["langs"][0][1] if s["langs"] else 1
    for i, (name, frac) in enumerate(s["langs"]):
        y = 124 + i * 20
        n, _ = text_path(name.upper(), JOST, 10.5, lx, y, tracking=0.16)
        p, _ = text_path(f"{frac * 100:.0f}%", MONO, 10.5, rx, y, anchor="end")
        bw = (rx - lx) * frac / top
        parts.append(
            f'<path d="{n}" fill="{ink}" fill-opacity=".88"/><path d="{p}" fill="{ink}" fill-opacity="{t["dim"]}"/>'
            f'<rect x="{lx}" y="{y + 5}" width="{rx - lx}" height="2" fill="{ink}" fill-opacity="{line}"/>'
            f'<rect x="{lx}" y="{y + 5}" width="{num(max(bw, 2))}" height="2" fill="{ink}" fill-opacity=".8"/>'
        )
    title = f"Telemetry: {s['contributions']} contributions in the past year, {s['repos']} public repositories"
    return svg(w, h, "".join(parts), "", title)


if __name__ == "__main__":
    login, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    stats = summarize(fetch(login, os.environ["GITHUB_TOKEN"]))
    for theme, t in THEMES.items():
        (out / f"telemetry-{theme}.svg").write_text(telemetry(t, stats), encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "weekly"}))
