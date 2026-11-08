"""README graphics for haashirk20/2023DEERHACKS (VocabVenture). Colours are sampled from the app's own
title art (images/title.png): cream #FBF1E3, green #47704C, orange #F4BF75 and blue #2476AE.
Card words and definitions are real rows from words.csv."""
from kit import W, box, frame, head, hero, kicker, lines, steps, text, tiles
from build import JOST, JOST_MED, MONO, SANS

THEMES = {
    "dark": {"bg": "#22362A", "ink": "#FBF1E3", "dim": 0.72, "line": 0.2, "accent": "#F4BF75", "panel": "#47704C"},
    "light": {"bg": "#FBF1E3", "ink": "#22362A", "dim": 0.68, "line": 0.18, "accent": "#2476AE", "panel": "#F4E2C4"},
}


def flashcards(t):
    """Two cards from the deck: the word side and, behind it, the flipped definition side."""
    x, y = 540, 70
    back = (f'<rect x="{x + 40}" y="{y}" width="250" height="160" rx="12" fill="#47704C"/>'
            + lines(t, "a state or condition markedly different from the norm", SANS, 14, x + 60, y + 50, 210, 20, color="#FBF1E3")[0]
            + text(t, "DEFINITION", JOST, 10, x + 60, y + 140, color="#FBF1E3", op=.7, tracking=0.24)[0])
    front = (f'<rect x="{x}" y="{y + 80}" width="250" height="160" rx="12" fill="#FBF1E3" stroke="#47704C" stroke-width="2"/>'
             + text(t, "aberration", JOST_MED, 28, x + 125, y + 168, color="#22362A", anchor="middle")[0]
             + text(t, "CLICK TO FLIP", JOST, 10, x + 125, y + 220, color="#2476AE", tracking=0.24, anchor="middle")[0])
    arrows = (f'<circle cx="{x + 80}" cy="{y + 285}" r="16" fill="#F4BF75"/><path d="M{x + 85} {y + 277}l-9 8 9 8z" fill="#22362A"/>'
              f'<circle cx="{x + 170}" cy="{y + 285}" r="16" fill="#F4BF75"/><path d="M{x + 165} {y + 277}l9 8-9 8z" fill="#22362A"/>')
    return back + front + arrows


def g_hero(t):
    return hero(t, "HACKATHON  ·  DEERHACKS 2023", "VocabVenture",
                "A desktop flashcard app for advanced English vocabulary, built in one weekend.",
                [("300", "words"), ("1", "pass per session"), ("3", "screens"), ("3", "teammates")],
                "Python · CustomTkinter · Pillow · PyInstaller", figure=flashcards)


def g_flow(t):
    h, y = head(t, "HOW IT WORKS", "A CSV file becomes a deck you flip through.")
    return frame(t, 290) + h + steps(t, [
        ("words.csv", "word,definition per line; swap in your own"),
        ("flashcards.py", "Flashcard per row, keyed by UUID"),
        ("Learn screen", "click the card to flip word and meaning"),
        ("Arrows", "right for the next card, left to go back"),
    ], 40, y, W - 80, accent=2)


def g_model(t):
    h, y = head(t, "CONTENT MODEL", "Built for more than one question type.")
    tl, bottom = tiles(t, [
        ("ContentBlock", "Base class: a UUID and a prompt."),
        ("Flashcard", "Adds the answer. The Learn screen uses these."),
        ("ChooseCorrectOption", "Holds shuffled multiple-choice options."),
    ], 40, y, W - 80, cols=3)
    qy = bottom + 40
    opts = ["of the most contemptible kind", "formally reject or disavow a formerly held belief",
            "fundamentally different or distinct in quality or kind", "the denial and rejection of a doctrine or belief"]
    out = [frame(t, 470), h, tl,
           kicker(t, "control.newQuestion()  ·  EXAMPLE FROM words.csv", 40, qy, accent=True),
           text(t, "abjure", JOST_MED, 22, 40, qy + 36)[0]]
    for i, o in enumerate(opts):
        ox, oy = 40 + (i % 2) * 410, qy + 56 + (i // 2) * 44
        right = i == 1
        out.append(box(t, ox, oy, 390, 36, accent=right, op=.9 if right else .25))
        out.append(text(t, o, SANS, 13, ox + 14, oy + 23, op=1 if right else .8)[0])
    out.append(text(t, "One card's definition plus three others drawn at random, shuffled. Not wired to a screen yet.", SANS, 13, 40, qy + 168, op=t["dim"])[0])
    return "".join(out)


GRAPHICS = {
    "hero": (400, g_hero, "VocabVenture: a desktop flashcard app with 300 words, built at DeerHacks 2023. Card example: aberration, a state or condition markedly different from the norm"),
    "how-it-works": (290, g_flow, "How it works: words.csv, flashcards.py builds the deck, the Learn screen flips cards, arrows move through the deck"),
    "content-model": (470, g_model, "Content model: ContentBlock, Flashcard and ChooseCorrectOption, and an example multiple-choice question for abjure"),
}
