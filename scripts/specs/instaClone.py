"""README graphics for haashirk20/instaClone. Colours are the app's own (lib/utils/colors.dart):
black #000000, web background #121212, search grey #262626, blue #0095F6 and white text."""
from kit import W, box, frame, head, hero, kicker, steps, text, tiles
from build import JOST, JOST_MED, MONO, SANS

THEMES = {
    "dark": {"bg": "#000000", "ink": "#FFFFFF", "dim": 0.66, "line": 0.2, "accent": "#0095F6", "panel": "#262626"},
    "light": {"bg": "#FFFFFF", "ink": "#121212", "dim": 0.62, "line": 0.14, "accent": "#0095F6", "panel": "#EFEFEF"},
}


def heart(x, y, s, color):
    """Material heart icon, s px wide, top-left at (x, y)."""
    k = s / 24
    return (f'<path transform="translate({x} {y}) scale({k:.3f})" fill="{color}" d="M12 21l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 '
            f'2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21z"/>')


def phone(t):
    """The feed on a phone: app bar, one post with a double-tap heart, likes and a caption, and the bottom bar."""
    x, y, w, h = 590, 26, 200, 348
    ink, accent = "#FFFFFF", "#0095F6"
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="26" fill="#000000" stroke="{t["ink"]}" stroke-opacity=".35" stroke-width="2"/>',
           text(t, "Instagram", JOST_MED, 15, x + 18, y + 40, color=ink)[0],
           f'<circle cx="{x + 30}" cy="{y + 70}" r="11" fill="#262626"/>',
           text(t, "username", SANS, 11, x + 48, y + 74, color=ink)[0],
           '<defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3A3A3A"/><stop offset="1" stop-color="#121212"/></linearGradient></defs>',
           f'<rect x="{x + 8}" y="{y + 90}" width="{w - 16}" height="150" fill="url(#pg)"/>',
           heart(x + w / 2 - 26, y + 140, 52, "#FFFFFF"),
           heart(x + 16, y + 250, 16, "#ED4956"),
           f'<rect x="{x + 42}" y="{y + 252}" width="14" height="12" rx="3" fill="none" stroke="{ink}"/>',
           text(t, "liked by you and others", SANS, 10, x + 16, y + 284, color=ink, op=.85)[0],
           text(t, "username  caption text", SANS, 10, x + 16, y + 300, color=ink, op=.7)[0],
           f'<rect x="{x + 8}" y="{y + h - 42}" width="{w - 16}" height="1" fill="#262626"/>']
    for i in range(5):
        out.append(f'<circle cx="{x + 30 + i * 35}" cy="{y + h - 22}" r="{6 if i else 7}" fill="{accent if i == 0 else "#FFFFFF"}" fill-opacity="{1 if i == 0 else .7}"/>')
    return "".join(out)


def g_hero(t):
    return hero(t, "FLUTTER + FIREBASE  ·  2023", "InstaClone",
                "A photo-sharing app modelled on Instagram, running on web and mobile from one codebase.",
                [("1", "codebase"), ("600 px", "layout switch"), ("3", "Firebase services"), ("0", "custom backend")],
                "Dart · Flutter · Firebase Auth, Firestore and Storage", figure=phone)


def g_data(t):
    h, y = head(t, "DATA MODEL", "Two collections, one subcollection, two storage folders.")
    cols = [
        ("FIRESTORE", "users/{uid}", ["uid, userName, email, bio", "photoUrl", "followers [ ]", "following [ ]"]),
        ("FIRESTORE", "posts/{postId}", ["uid, userName, profImage", "description, postUrl", "datePublished", "likes [ ]"]),
        ("SUBCOLLECTION", "posts/{postId}/comments", ["commentId, uid, name", "profilePic, text", "datePublished"]),
        ("STORAGE", "Firebase Storage", ["profilepics/<uid>", "posts/<uid>/<uuid>"]),
    ]
    out = [frame(t, 380), h]
    cw = (W - 80 - 3 * 16) / 4
    for i, (title, path, fields) in enumerate(cols):
        cx = 40 + i * (cw + 16)
        out.append(kicker(t, title, cx, y, accent=i == 3))
        out.append(text(t, path, MONO, 11.5, cx, y + 20, op=.92)[0])
        for j, f in enumerate(fields):
            out.append(box(t, cx, y + 34 + j * 34, cw, 28, op=.24))
            out.append(text(t, f, MONO, 11, cx + 10, y + 52 + j * 34, op=.92)[0])
    out.append(text(t, "followers, following and likes change with FieldValue.arrayUnion and arrayRemove.", SANS, 13.5, 40, y + 202, op=.8)[0])
    return "".join(out)


def g_arch(t):
    h, y = head(t, "ARCHITECTURE", "Screens never write to Firebase directly.")
    return frame(t, 300) + h + steps(t, [
        ("main.dart", "authStateChanges() picks login or home"),
        ("ResponsiveLayout", "LayoutBuilder: over 600 px is desktop"),
        ("Screens", "feed, search, add post, profile, comments"),
        ("UserProvider", "signed-in user, loaded once"),
        ("resources/", "Auth, Firestore and Storage methods"),
    ], 40, y, W - 80, accent=4)


def g_features(t):
    h, y = head(t, "FEATURES", "The core Instagram loop.")
    tl, _ = tiles(t, [
        ("Accounts", "Email and password sign-up and login with Firebase Auth, with a profile photo and bio."),
        ("Posting", "Pick from the camera or gallery, add a caption, upload to Storage and save to Firestore."),
        ("Live feed", "A Firestore snapshots() stream, so new posts appear without a refresh."),
        ("Likes and comments", "Double-tap to like with a heart animation; comments sorted newest first."),
        ("Follow and search", "Follow lists kept on both users; search by name and a quilted explore grid."),
        ("Responsive", "A separate desktop layout above 600 px that switches live as the window resizes."),
    ], 40, y, W - 80, cols=3)
    return frame(t, 410) + h + tl


GRAPHICS = {
    "hero": (400, g_hero, "InstaClone: a Flutter and Firebase photo-sharing app on web and mobile, with a layout switch at 600 px and no custom backend"),
    "data-model": (380, g_data, "Data model: users and posts collections, a comments subcollection, and Storage folders for profile pictures and posts"),
    "architecture": (300, g_arch, "Architecture: main.dart auth listener, ResponsiveLayout, screens, UserProvider, and resources classes for Firebase"),
    "features": (410, g_features, "Features: accounts, posting, live feed, likes and comments, follow and search, responsive layout"),
}
