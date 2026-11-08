"""README graphics for haashirk20/spotify-bud. The bot has no UI of its own, so the colours are Spotify's:
green #1DB954 on #121212 with #282828 surfaces. Bot replies are the real strings from lib/app.py."""
from kit import W, box, fillrect, frame, head, hero, kicker, lines, steps, text
from build import JOST, JOST_MED, MONO, SANS

THEMES = {
    "dark": {"bg": "#121212", "ink": "#FFFFFF", "dim": 0.66, "line": 0.18, "accent": "#1DB954", "panel": "#282828"},
    "light": {"bg": "#FFFFFF", "ink": "#191414", "dim": 0.64, "line": 0.14, "accent": "#1AA34A", "panel": "#EEF8F1"},
}


def bubble(t, s, x, y, me, w_max=250):
    """A chat bubble: wrapped text, green when sent by the user."""
    tw = min(w_max, text(t, s, SANS, 12, 0, 0)[1] + 26)
    h = lines(t, s, SANS, 12, 0, 0, tw - 22, 17)[1] + 26
    bx = x - tw if me else x
    fill = f'fill="{t["accent"]}"' if me else f'fill="{t["ink"]}" fill-opacity=".1"'
    body = lines(t, s, SANS, 12, bx + 12, y + 20, tw - 22, 17, color="#121212" if me else None)[0]
    return f'<rect x="{bx}" y="{y}" width="{tw}" height="{h}" rx="10" {fill}/>' + body, h


def chat(t):
    """A Telegram chat with the bot: one /playlist request and its reply, and an argument prompt."""
    x, y, w, h = 520, 40, 320, 320
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{t["panel"]}"/>',
           f'<circle cx="{x + 30}" cy="{y + 30}" r="12" fill="{t["accent"]}"/>',
           text(t, "Spotifybud", JOST_MED, 14, x + 52, y + 35)[0],
           text(t, "EXAMPLE", JOST, 10, x + w - 20, y + 34, op=.6, tracking=0.24, anchor="end")[0],
           fillrect(t, x, y + 58, w, 1, t["line"])]
    my = y + 76
    for s, me in (("/playlist", True), ("What genre/artist/song would you like a playlist for?", False),
                  ("/playlist lofi hip hop", True), ("Here is the playlist link: https://open.spotify.com/playlist/...", False)):
        svg, bh = bubble(t, s, x + w - 18 if me else x + 18, my, me)
        out.append(svg)
        my += bh + 12
    return "".join(out)


def g_hero(t):
    return hero(t, "TELEGRAM BOT  ·  PYTHON  ·  2023", "Spotifybud",
                "Convert SoundCloud playlists to Spotify, get a song recommendation, or build a playlist from one search.",
                [("4", "commands"), ("10", "tracks per playlist"), ("2", "music services")],
                "python-telegram-bot · Spotipy · soundcloud-lib", figure=chat)


CMDS = [
    ("/convert <link>", "a Spotify playlist named after the SoundCloud one, as a link"),
    ("/recommend <song>", 'if you like "<song>" you should listen to "<artist> - <track>" at <link>'),
    ("/playlist <query>", "Here is the playlist link: <link>"),
    ("/help", "the list of commands"),
]


def g_commands(t):
    h, y = head(t, "COMMANDS", "Four commands, each answered with a link.")
    out = [frame(t, 400), h, fillrect(t, 40, y, W - 80, 1, t["line"])]
    for i, (cmd, reply) in enumerate(CMDS):
        ry = y + i * 50
        out.append(text(t, cmd, MONO, 13.5, 40, ry + 31, color=t["accent"])[0])
        out.append(text(t, reply, SANS, 13, 250, ry + 31, op=.85)[0])
        out.append(fillrect(t, 40, ry + 50, W - 80, 1, t["line"]))
    out.append(text(t, "A command with no argument asks for one. Any other message points to /help.", SANS, 13, 40, y + 236, op=t["dim"])[0])
    return "".join(out)


def g_convert(t):
    h, y = head(t, "CONVERTING A PLAYLIST", "Each SoundCloud track is matched by a Spotify search.")
    return (frame(t, 300) + h + steps(t, [
        ("SoundCloud link", "/convert followed by a playlist URL"),
        ("api.resolve", "sclib loads the playlist and tracks"),
        ("Search Spotify", "\"artist title\", first result taken"),
        ("New playlist", "title plus a 5-character suffix"),
        ("Reply", "the playlist's Spotify link"),
    ], 40, y, W - 80, accent=2)
        + text(t, "A bad link replies \"Invalid URL\". A track with no Spotify result stops the conversion.", SANS, 13, 40, y + 140, op=t["dim"])[0])


def node(t, x, y, w, h, title, sub, accent=False):
    return (box(t, x, y, w, h, accent=accent)
            + text(t, title, JOST_MED, 15, x + 16, y + 28)[0]
            + lines(t, sub, MONO, 11, x + 16, y + 48, w - 32, 16, op=t["dim"])[0])


def arrow(t, x1, y1, x2, y2):
    return f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{t["ink"]}" stroke-opacity=".4"/>'


def g_arch(t):
    h, y = head(t, "ARCHITECTURE", "One router for Telegram, one module for the music APIs.")
    out = [frame(t, 410), h]
    out.append(node(t, 40, y + 40, 170, 84, "Telegram chat", "long polling"))
    out.append(node(t, 250, y + 40, 180, 84, "lib/app.py", "routes each command by name"))
    out.append(node(t, 470, y + 40, 180, 84, "lib/spotify_api.py", "search, recommend, create playlist", accent=True))
    out.append(node(t, 690, y, 150, 74, "Spotify Web API", "OAuth, public playlists only"))
    out.append(node(t, 690, y + 94, 150, 74, "SoundCloud", "resolve playlist"))
    out.append(node(t, 250, y + 160, 400, 52, "lib/auth.py  (gitignored)", "bot token and Spotify app credentials"))
    out += [arrow(t, 210, y + 82, 250, y + 82), arrow(t, 430, y + 82, 470, y + 82),
            arrow(t, 650, y + 70, 690, y + 37), arrow(t, 650, y + 94, 690, y + 131),
            arrow(t, 340, y + 124, 340, y + 160), arrow(t, 560, y + 124, 560, y + 160)]
    return "".join(out)


GRAPHICS = {
    "hero": (400, g_hero, "Spotifybud: a Telegram bot with 4 commands that converts SoundCloud playlists to Spotify, recommends songs and builds 10-track playlists. Example chat with a /playlist request"),
    "commands": (400, g_commands, "Commands: /convert, /recommend, /playlist and /help, with the bot's reply to each"),
    "convert": (300, g_convert, "Converting a playlist: SoundCloud link, resolve with sclib, search Spotify for each track, create a playlist with a 5-character suffix, reply with the link"),
    "architecture": (410, g_arch, "Architecture: Telegram chat, lib/app.py command router, lib/spotify_api.py, Spotify Web API and SoundCloud, with credentials in a gitignored lib/auth.py"),
}
