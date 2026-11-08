"""README graphics for haashirk20/snake-cake. Colours are the game's own: board tiles #AAD751 and
#A2D149, snake #4674E9, and the colour-blind palette #ECECEC, #AFA6A6 and #000000 (SnakeView.java)."""
from kit import W, frame, head, hero, kicker, rows, text, tiles
from build import JOST, MONO

THEMES = {
    "dark": {"bg": "#1E2B14", "ink": "#F2F8E6", "dim": 0.7, "line": 0.18, "accent": "#AAD751", "panel": "#2C3F1D"},
    "light": {"bg": "#F3F8E7", "ink": "#1E2B14", "dim": 0.66, "line": 0.16, "accent": "#4674E9", "panel": "#E3EFC8"},
}


def board(x, y, n, size, c1, c2, snake_color, body, cake):
    """A slice of the game board: checkered tiles, the snake's body cells and a cake tile."""
    out = []
    for r in range(n):
        for c in range(n):
            out.append(f'<rect x="{x + c * size}" y="{y + r * size}" width="{size}" height="{size}" fill="#{c1 if (r + c) % 2 == 0 else c2}"/>')
    for i, (c, r) in enumerate(body):
        out.append(f'<rect x="{x + c * size + 2}" y="{y + r * size + 2}" width="{size - 4}" height="{size - 4}" rx="5" fill="#{snake_color}" opacity="{1 if i == 0 else .9}"/>')
    hc, hr = body[0]
    out.append(f'<circle cx="{x + hc * size + size * .68}" cy="{y + hr * size + size * .35}" r="3" fill="#fff"/>')
    cc, cr = cake
    cx, cy = x + cc * size, y + cr * size
    out.append(f'<rect x="{cx + 6}" y="{cy + size * .42}" width="{size - 12}" height="{size * .42}" rx="3" fill="#F4C7A1"/>'
               f'<rect x="{cx + 6}" y="{cy + size * .36}" width="{size - 12}" height="{size * .14}" rx="3" fill="#F77FA8"/>'
               f'<rect x="{cx + size / 2 - 1.5}" y="{cy + size * .16}" width="3" height="{size * .2}" fill="#E8463A"/>')
    return f'<g>{"".join(out)}<rect x="{x}" y="{y}" width="{n * size}" height="{n * size}" fill="none" stroke="#000" stroke-opacity=".15"/></g>'


SNAKE = [(5, 3), (4, 3), (3, 3), (3, 4), (3, 5), (2, 5)]


def g_hero(t):
    return hero(t, "JAVAFX GAME  ·  CSC207  ·  2022", "Snake Cake",
                "Steer the snake to the cake, dodge the walls and your own tail, and land on a saved leaderboard.",
                [("20×20", "board"), ("100 ms", "per tick"), ("2", "palettes"), ("4", "teammates")],
                "Java · JavaFX Canvas, Timeline and FXML",
                figure=lambda t: board(540, 60, 7, 40, "AAD751", "A2D149", "4674E9", SNAKE, (5, 1)))


def g_controls(t):
    h, y = head(t, "HOW TO PLAY", "Three controls and two rules.")
    return frame(t, 390) + h + rows(t, [
        ("Steer with the arrow keys or WASD", "ARROWS / WASD", True),
        ("Pause and resume", "P", False),
        ("Toggle colour-blind mode", "C", False),
        ("The snake can't reverse into itself", "rule", False),
        ("Cake spawns on a random free tile, never on the snake", "rule", False),
    ], 40, y, W - 80, row=48)


def g_palettes(t):
    h, y = head(t, "COLOUR-BLIND MODE", "One key swaps the palette, not the drawing code.")
    return (frame(t, 400) + h
            + kicker(t, "DEFAULT", 40, y, accent=True)
            + board(40, y + 14, 6, 34, "AAD751", "A2D149", "4674E9", [(3, 2), (2, 2), (1, 2), (1, 3)], (4, 4))
            + text(t, "#AAD751  #A2D149  snake #4674E9", MONO, 11, 40, y + 236, op=t["dim"])[0]
            + kicker(t, "COLOUR-BLIND  ·  PRESS C", 460, y)
            + board(460, y + 14, 6, 34, "ECECEC", "AFA6A6", "000000", [(3, 2), (2, 2), (1, 2), (1, 3)], (4, 4))
            + text(t, "#ECECEC  #AFA6A6  snake #000000", MONO, 11, 460, y + 236, op=t["dim"])[0])


def g_arch(t):
    h, y = head(t, "ARCHITECTURE", "Rules, screens and scores live in separate packages.")
    tl, _ = tiles(t, [
        ("snakeModel", "Game holds the Snake, Food and GameBoard. It checks wall and self collisions and handles eating."),
        ("View", "SnakeView builds the menu, runs the 100 ms Timeline and draws the Canvas. LoadView lists saved games."),
        ("leaderBoard", "Player compares by score. LeaderBoardFile reads, sorts and writes leaderBoard.txt; Controller.fxml shows the table."),
    ], 40, y, W - 80, cols=3)
    return frame(t, 310) + h + tl


GRAPHICS = {
    "hero": (400, g_hero, "Snake Cake: a JavaFX Snake game on a 20 by 20 board, 100 ms per tick, two palettes, four teammates"),
    "controls": (390, g_controls, "Arrow keys or WASD steer, P pauses, C toggles colour-blind mode; no reversing; cake spawns on a free tile"),
    "palettes": (400, g_palettes, "Default palette: green tiles and a blue snake. Colour-blind palette: grey tiles and a black snake"),
    "architecture": (310, g_arch, "Packages: snakeModel for rules, View for screens and the game loop, leaderBoard for scores"),
}
