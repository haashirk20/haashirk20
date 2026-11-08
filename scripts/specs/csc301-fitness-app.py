"""README graphics for haashirk20/csc301-fitness-app. Colours are the site's own (website/css/style.css):
navy #00006D, indigo #1700A7 and grey #878787. The worked example runs app/calorie.py's formula."""
import math

from kit import W, frame, head, hero, kicker, rows, steps, text
from build import JOST, JOST_MED, MONO, SANS

THEMES = {
    "dark": {"bg": "#00006D", "ink": "#FFFFFF", "dim": 0.72, "line": 0.2, "accent": "#9F94FF", "panel": "#1700A7"},
    "light": {"bg": "#F4F3FC", "ink": "#00006D", "dim": 0.66, "line": 0.15, "accent": "#1700A7", "panel": "#E3E0F8"},
}

# 25-year-old male, 180 cm, 75 kg, moderately active, maintain: BMR 1,755, x1.55 = 2,720 (int).
TARGET, EATEN = 2720, 900


def tracker(t):
    """The calorie page: a ring for calories left out of the daily target, with log and reset buttons."""
    x, y, w, h = 540, 56, 290, 292
    cx, cy, r = x + w / 2, y + 128, 74
    frac = (TARGET - EATEN) / TARGET
    a = 2 * math.pi * frac
    ex, ey = cx + r * math.sin(a), cy - r * math.cos(a)
    big = 1 if frac > .5 else 0
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{t["panel"]}"/>'
            + text(t, "TODAY  ·  EXAMPLE", JOST, 10, x + 20, y + 30, op=.75, tracking=0.24)[0]
            + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["ink"]}" stroke-opacity=".18" stroke-width="12"/>'
            + f'<path d="M{cx} {cy - r}A{r} {r} 0 {big} 1 {ex:.1f} {ey:.1f}" fill="none" stroke="{t["accent"]}" stroke-width="12" stroke-linecap="round"/>'
            + text(t, f"{TARGET - EATEN:,}", JOST_MED, 28, cx, cy + 6, anchor="middle")[0]
            + text(t, "KCAL LEFT", JOST, 10, cx, cy + 26, op=.75, tracking=0.2, anchor="middle")[0]
            + text(t, f"Daily target {TARGET:,} kcal", SANS, 12.5, cx, y + 232, op=.85, anchor="middle")[0]
            + f'<rect x="{x + 20}" y="{y + 248}" width="120" height="30" rx="6" fill="{t["bg"]}"/>'
            + text(t, "Log calories", JOST_MED, 12.5, x + 80, y + 268, anchor="middle")[0]
            + f'<rect x="{x + 150}" y="{y + 248}" width="120" height="30" rx="6" fill="none" stroke="{t["ink"]}" stroke-opacity=".4"/>'
            + text(t, "Reset", JOST_MED, 12.5, x + 210, y + 268, anchor="middle")[0])


def g_hero(t):
    return hero(t, "FULL-STACK WEB APP  ·  CSC301  ·  2024", "CSC301\nFitness App",
                "Accounts, a daily calorie budget from the Mifflin-St Jeor equation, and a BMI calculator.",
                [("7", "API routes"), ("5", "activity levels"), ("bcrypt", "passwords"), ("6", "teammates")],
                "Flask · Firebase Realtime Database · Bootstrap", figure=tracker)


def g_calories(t):
    h, y = head(t, "THE DAILY TARGET", "Three steps from your profile to a calorie budget.")
    return (frame(t, 340) + h + steps(t, [
        ("Mifflin-St Jeor BMR", "10w + 6.25h - 5a + 5 (male) or - 161 (female)"),
        ("Activity multiplier", "1.2, 1.375, 1.55, 1.725 or 1.9"),
        ("Goal", "gain +500 kcal, lose x0.8, maintain x1"),
        ("Saved target", "stored with the user; meals subtract from it"),
    ], 40, y, W - 80, h=112, accent=3)
        + kicker(t, "WORKED EXAMPLE", 40, y + 150)
        + text(t, "Male, 25, 180 cm, 75 kg, moderately active, maintain:  BMR 1,755  x 1.55  =  2,720 kcal a day",
               MONO, 12, 40, y + 174, op=.9)[0])


ROUTES = [
    ("POST  /api/signup", "create an account"), ("POST  /api/login", "log in, start a session"),
    ("GET   /api/calories", "target and calories left"), ("POST  /api/calories", "calculate and save the target"),
    ("POST  /api/calories/reduce", "log calories eaten"), ("POST  /api/calories/reset", "reset to the target"),
    ("POST  /api/bmi", "BMI and its category"),
]


def g_routes(t):
    h, y = head(t, "API", "Seven routes. Every one after login needs a session.")
    out = [frame(t, 500), h]
    out.append(rows(t, [(r, n, i < 2) for i, (r, n) in enumerate(ROUTES)], 40, y, W - 80, row=46))
    return "".join(out)


def g_arch(t):
    h, y = head(t, "ARCHITECTURE", "Calculations stay free of Flask and Firebase.")
    return frame(t, 290) + h + steps(t, [
        ("website/", "four pages that call the API with fetch"),
        ("Flask API", "app/routes.py validates input, returns 400 or 401"),
        ("Calculators", "calorie.py and calculators.py, plain functions"),
        ("User model", "app/models.py wraps every Firebase call"),
        ("Firebase", "Realtime Database, users/"),
    ], 40, y, W - 80, accent=2)


GRAPHICS = {
    "hero": (400, g_hero, "CSC301 Fitness App: 7 API routes, 5 activity levels, bcrypt passwords, 6 teammates. Example calorie page with a ring of calories left"),
    "calories": (340, g_calories, "Daily target: Mifflin-St Jeor BMR, times an activity multiplier from 1.2 to 1.9, then the goal adjustment; example 2,720 kcal"),
    "api": (500, g_routes, "API routes: signup, login, get and post calories, reduce, reset, and BMI"),
    "architecture": (290, g_arch, "Architecture: static website, Flask API, calculator functions, User model, Firebase Realtime Database"),
}
