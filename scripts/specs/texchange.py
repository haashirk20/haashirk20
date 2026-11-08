"""README graphics for haashirk20/texchange. Colours come from frontend/src/styles.css: the page
background gradient #17153b to rgb(72, 10, 187), white message cards and #212121 text."""
from kit import W, fillrect, frame, head, hero, steps, text, tiles
from build import JOST, JOST_MED, MONO, SANS

THEMES = {
    "dark": {"bg": "#17153B", "ink": "#FFFFFF", "dim": 0.7, "line": 0.18, "accent": "#A98BFF", "panel": "#480ABB"},
    "light": {"bg": "#F6F4FD", "ink": "#17153B", "dim": 0.66, "line": 0.15, "accent": "#480ABB", "panel": "#E6DEFA"},
}


def chat(t):
    """The chat screen: gradient panel, server notices and anonymous messages, and the Swap button.
    The two system lines are the server's real messages from backend/server.js."""
    x, y, w, h = 520, 52, 320, 296
    msgs = [("You have been paired! Start chatting.", "sys"), ("Anonymous: hey, where are you from?", "them"),
            ("You: Toronto. You?", "me"), ("Your chat partner left. Searching for a new match...", "sys")]
    out = [f'<defs><linearGradient id="cg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#17153B"/><stop offset="1" stop-color="#480ABB"/></linearGradient></defs>'
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="url(#cg)" stroke="#FFFFFF" stroke-opacity=".18"/>',
           text(t, "TexChange", JOST_MED, 15, x + 18, y + 30, color="#FFFFFF")[0]]
    my = y + 56
    for s, kind in msgs:
        if kind == "sys":
            out.append(text(t, s, SANS, 10.5, x + w / 2, my + 14, color="#FFFFFF", op=.7, anchor="middle")[0])
            my += 30
            continue
        tw = text(t, s, SANS, 12, 0, 0)[1] + 24
        bx = x + w - 18 - tw if kind == "me" else x + 18
        out.append(f'<rect x="{bx}" y="{my}" width="{tw}" height="30" rx="8" fill="#FFFFFF" fill-opacity="{1 if kind == "me" else .9}"/>')
        out.append(text(t, s, SANS, 12, bx + 12, my + 19, color="#212121")[0])
        my += 40
    out.append(f'<rect x="{x + 18}" y="{y + h - 50}" width="{w - 120}" height="32" rx="8" fill="#FFFFFF" fill-opacity=".92"/>')
    out.append(text(t, "Type a message", SANS, 12, x + 30, y + h - 29, color="#212121", op=.5)[0])
    out.append(f'<rect x="{x + w - 92}" y="{y + h - 50}" width="74" height="32" rx="8" fill="#FFFFFF" fill-opacity=".18" stroke="#FFFFFF" stroke-opacity=".5"/>')
    out.append(text(t, "Swap", JOST_MED, 13, x + w - 55, y + h - 29, color="#FFFFFF", anchor="middle")[0])
    return "".join(out)


def g_hero(t):
    return hero(t, "REAL-TIME WEB APP  ·  2024", "TexChange",
                "Anonymous text chat roulette. Open the page, get paired with a stranger, swap whenever you like.",
                [("1:1", "private rooms"), ("FIFO", "matchmaking"), ("2", "routes"), ("3", "teammates")],
                "React · Express · Socket.IO · Docker Compose", figure=chat)


def g_flow(t):
    h, y = head(t, "MATCHMAKING", "Longest wait gets matched first.")
    return frame(t, 290) + h + steps(t, [
        ("Connect", "open /chat, Socket.IO client connects"),
        ("Queue", "socket added to a Set of waiting users"),
        ("matchUsers", "first two in insertion order"),
        ("Private room", "room-uuid, match_room sent to both"),
        ("Swap or leave", "swap re-queues both, leave re-queues one"),
    ], 40, y, W - 80, accent=2)


def g_sequence(t):
    """A sequence diagram: User A, server and User B lanes, with the real Socket.IO events."""
    h, y = head(t, "MESSAGE FLOW", "The server relays each message to the other socket only.")
    lanes = {"A": 140, "S": 440, "B": 740}
    top = y + 6
    out = [frame(t, 540), h]
    for key, label in (("A", "User A  ·  React"), ("S", "Server  ·  Express + Socket.IO"), ("B", "User B  ·  React")):
        lx = lanes[key]
        lw = text(t, label, JOST_MED, 13, 0, 0)[1] + 28
        out.append(f'<rect x="{lx - lw / 2}" y="{top}" width="{lw}" height="30" rx="4" fill="{t["panel"]}"/>')
        out.append(text(t, label, JOST_MED, 13, lx, top + 20, anchor="middle")[0])
        out.append(f'<path d="M{lx} {top + 30}V{top + 412}" stroke="{t["ink"]}" stroke-opacity=".25" stroke-dasharray="3 4"/>')
    events = [("A", "S", "connect", False), ("B", "S", "connect  ·  matchUsers()", False),
              ("S", "A", "match_room (room-uuid)", True), ("S", "B", "match_room (room-uuid)", True),
              ("A", "S", "send_message {room, message}", False), ("S", "B", "receive_message  \"Anonymous: …\"", True),
              ("B", "S", "swap", False), ("S", "S", "both leave the room, rejoin the queue", False)]
    for i, (a, b, label, reply) in enumerate(events):
        ey = top + 70 + i * 46
        x1, x2 = lanes[a], lanes[b]
        col = t["accent"] if reply else t["ink"]
        if a == b:
            out.append(f'<path d="M{x1} {ey - 8}h40v16h-36" fill="none" stroke="{col}" stroke-opacity=".8"/>')
            out.append(text(t, label, MONO, 11.5, x1 + 52, ey + 4, op=.9)[0])
            continue
        d = 1 if x2 > x1 else -1
        dash = ' stroke-dasharray="5 4"' if reply else ""
        out.append(f'<path d="M{x1} {ey}H{x2 - d * 6}" stroke="{col}" stroke-opacity=".85"{dash}/>'
                   f'<path d="M{x2 - d * 8} {ey - 4}L{x2} {ey}L{x2 - d * 8} {ey + 4}z" fill="{col}"/>')
        out.append(text(t, label, MONO, 11.5, (x1 + x2) / 2, ey - 8, op=.92, anchor="middle")[0])
    return "".join(out)


def g_features(t):
    h, y = head(t, "FEATURES", "Everything happens without a reload.")
    tl, _ = tiles(t, [
        ("Automatic matchmaking", "Users are paired as soon as two are waiting, with a loading screen in between."),
        ("Anonymous messages", "The sender sees \"You:\" and the recipient sees \"Anonymous:\". No names are attached."),
        ("Swap", "One button sends both people back to the queue to find new partners."),
        ("Partner-left handling", "The remaining user is told, and re-queued in the same disconnect handler."),
    ], 40, y, W - 80, cols=2)
    return frame(t, 380) + h + tl


GRAPHICS = {
    "hero": (400, g_hero, "TexChange: anonymous one-to-one chat roulette with FIFO matchmaking, built with React, Express and Socket.IO"),
    "matchmaking": (290, g_flow, "Matchmaking: connect, join a Set-based queue, matchUsers pairs the first two, a private UUID room, swap or leave re-queues"),
    "message-flow": (540, g_sequence, "Message flow between User A, the server and User B: connect, match_room, send_message, receive_message, swap"),
    "features": (380, g_features, "Features: automatic matchmaking, anonymous messages, swap, partner-left handling"),
}
