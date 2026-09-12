#!/usr/bin/env python3
"""Fullscreen Matrix wake-up: digital rain, Morpheus, red/blue pill."""

from __future__ import annotations

import atexit
import os
import random
import select
import shutil
import subprocess
import sys
import termios
import time
import tty
from pathlib import Path

HOME = Path.home()
WALLPAPERS = HOME / ".config/omarchy/matrix/wallpapers"
RED_BG = WALLPAPERS / "red-pill.png"
BLUE_BG = WALLPAPERS / "blue-pill.png"

GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789#$%&*+"

ESC = "\033"
RESET = f"{ESC}[0m"
HIDE = f"{ESC}[?25l"
SHOW = f"{ESC}[?25h"
ALT_ON = f"{ESC}[?1049h"
ALT_OFF = f"{ESC}[?1049l"
CLEAR = f"{ESC}[2J{ESC}[H"
BLACK_BG = f"{ESC}]11;#000000{ESC}\\"
GREEN_FG = f"{ESC}]10;#00ff41{ESC}\\"


def rgb(r: int, g: int, b: int) -> str:
    return f"{ESC}[38;2;{r};{g};{b}m"


def bg(r: int, g: int, b: int) -> str:
    return f"{ESC}[48;2;{r};{g};{b}m"


G = rgb(0, 255, 65)
G_DIM = rgb(0, 90, 20)
G_MID = rgb(0, 170, 40)
G_BRIGHT = rgb(180, 255, 180)
RED = rgb(220, 24, 32)
RED_GLOW = rgb(255, 90, 90)
BLUE = rgb(40, 120, 255)
BLUE_GLOW = rgb(140, 200, 255)
WHITE = rgb(230, 230, 230)
MUTED = rgb(90, 110, 90)

_fd = sys.stdin.fileno()
_old_term: list | None = None
_raw = False


def size() -> tuple[int, int]:
    cols, rows = shutil.get_terminal_size((80, 24))
    return max(rows, 12), max(cols, 40)


def wait_for_fullscreen() -> None:
    deadline = time.time() + 2.0
    while time.time() < deadline:
        rows, cols = size()
        if not (rows == 24 and cols == 80):
            return
        time.sleep(0.03)


def setup() -> None:
    global _old_term, _raw
    sys.stdout.write(ALT_ON + HIDE + BLACK_BG + GREEN_FG + CLEAR)
    sys.stdout.flush()
    _old_term = termios.tcgetattr(_fd)
    tty.setcbreak(_fd)
    _raw = True


def restore() -> None:
    global _raw
    try:
        if _old_term is not None:
            termios.tcsetattr(_fd, termios.TCSADRAIN, _old_term)
        _raw = False
        sys.stdout.write(SHOW + ALT_OFF + RESET + f"{ESC}[?1049l")
        sys.stdout.flush()
    except Exception:
        pass


def move(row: int, col: int) -> str:
    return f"{ESC}[{max(1, row)};{max(1, col)}H"


def flush() -> None:
    sys.stdout.flush()


def key_waiting(timeout: float = 0.0) -> str | None:
    ready, _, _ = select.select([sys.stdin], [], [], timeout)
    if not ready:
        return None
    ch = os.read(_fd, 1).decode("utf-8", "ignore")
    if ch != "\x1b":
        return ch
    rest = ""
    if select.select([sys.stdin], [], [], 0.02)[0]:
        rest = os.read(_fd, 8).decode("utf-8", "ignore")
    if rest.startswith("[C") or rest.startswith("OC"):
        return "RIGHT"
    if rest.startswith("[D") or rest.startswith("OD"):
        return "LEFT"
    if rest.startswith("[A") or rest.startswith("OA"):
        return "UP"
    if rest.startswith("[B") or rest.startswith("OB"):
        return "DOWN"
    return "ESC"


def drain_keys() -> None:
    while key_waiting(0) is not None:
        pass


def typewriter(row: int, col: int, text: str, color: str = G, delay: float = 0.038) -> None:
    for i, ch in enumerate(text):
        sys.stdout.write(move(row, col + i) + color + ch + RESET)
        flush()
        if ch != " ":
            time.sleep(delay * random.uniform(0.55, 1.45))
        else:
            time.sleep(delay * 0.35)
        if key_waiting(0) is not None:
            sys.stdout.write(move(row, col) + color + text + RESET)
            flush()
            drain_keys()
            return
    time.sleep(0.12)


def center_col(text: str, cols: int) -> int:
    return max(1, (cols - len(text)) // 2 + 1)


def put_centered(row: int, text: str, color: str, cols: int) -> None:
    sys.stdout.write(move(row, center_col(text, cols)) + color + text + RESET)


def rain(duration: float = 4.2) -> None:
    rows, cols = size()
    heads = [random.randint(-rows, 0) for _ in range(cols)]
    speeds = [random.choice((1, 1, 1, 2)) for _ in range(cols)]
    trail = [random.randint(6, 16) for _ in range(cols)]
    start = time.time()
    while time.time() - start < duration:
        rows, cols = size()
        if len(heads) != cols:
            heads = [random.randint(-rows, 0) for _ in range(cols)]
            speeds = [random.choice((1, 1, 1, 2)) for _ in range(cols)]
            trail = [random.randint(6, 16) for _ in range(cols)]
        buf = [move(1, 1)]
        grid = [[" "] * cols for _ in range(rows)]
        colors = [[G_DIM] * cols for _ in range(rows)]
        for x in range(cols):
            heads[x] += speeds[x]
            if heads[x] - trail[x] > rows:
                heads[x] = random.randint(-12, 0)
                trail[x] = random.randint(6, 16)
            for t in range(trail[x]):
                y = heads[x] - t
                if 0 <= y < rows:
                    grid[y][x] = random.choice(GLYPHS)
                    if t == 0:
                        colors[y][x] = G_BRIGHT
                    elif t < 3:
                        colors[y][x] = G
                    elif t < 7:
                        colors[y][x] = G_MID
                    else:
                        colors[y][x] = G_DIM
        for y, line in enumerate(grid):
            buf.append(move(y + 1, 1))
            last = None
            for x, ch in enumerate(line):
                c = colors[y][x]
                if c != last:
                    buf.append(c)
                    last = c
                buf.append(ch)
        sys.stdout.write("".join(buf))
        flush()
        if key_waiting(0.045) is not None:
            drain_keys()
            break


def flash(color: str, times: int = 2) -> None:
    rows, cols = size()
    for _ in range(times):
        sys.stdout.write(move(1, 1) + color + (" " * cols * min(rows, 3)))
        flush()
        time.sleep(0.05)
        sys.stdout.write(CLEAR)
        flush()
        time.sleep(0.05)


def capsule_rows(inner: tuple[int, int, int], highlight: tuple[int, int, int], width: int = 22) -> list[str]:
    """Build a glossy two-tone capsule using truecolor background cells."""
    hi = bg(*highlight) + " "
    lo = bg(*inner) + " "
    empty = " "
    rows = []
    for pad, fill in ((4, width - 8), (2, width - 4), (1, width - 2), (0, width), (0, width), (1, width - 2), (2, width - 4), (4, width - 8)):
        split = fill // 2
        body = (hi * split) + (lo * (fill - split))
        rows.append(empty * pad + body + RESET + empty * pad)
    return rows


def draw_pill(top: int, left: int, kind: str, selected: bool) -> None:
    if kind == "red":
        body, glow, label = RED, RED_GLOW, "PILULE ROUGE"
        inner, highlight = (140, 6, 14), (230, 50, 55)
    else:
        body, glow, label = BLUE, BLUE_GLOW, "PILULE BLEUE"
        inner, highlight = (16, 55, 175), (80, 160, 255)

    frame = G_BRIGHT if selected else MUTED
    width = 32
    sys.stdout.write(move(top, left) + frame + ("╔" if selected else "┌") + ("═" if selected else "─") * width + ("╗" if selected else "┐") + RESET)
    art = capsule_rows(inner, highlight, 24)
    for i, line in enumerate(art):
        side = "║" if selected else "│"
        sys.stdout.write(move(top + 1 + i, left) + frame + side + "    " + line + frame + "    " + side + RESET)
    sys.stdout.write(
        move(top + 1 + len(art), left)
        + frame
        + ("╚" if selected else "└")
        + ("═" if selected else "─") * width
        + ("╝" if selected else "┘")
        + RESET
    )
    lab = f"▸ {label} ◂" if selected else f"  {label}  "
    sys.stdout.write(move(top + 2 + len(art), left + 7) + (glow if selected else body) + lab + RESET)
    hint = "ENTRÉE POUR AVALER" if selected else "                  "
    sys.stdout.write(move(top + 3 + len(art), left + 7) + (G if selected else MUTED) + hint + RESET)


def draw_choice(selected: str) -> None:
    rows, cols = size()
    sys.stdout.write(CLEAR)
    title = "CECI EST TA DERNIÈRE CHANCE."
    put_centered(3, title, G_BRIGHT, cols)
    put_centered(5, "This is your last chance.", G_DIM, cols)

    quotes = [
        (RED_GLOW, "La pilule bleue : l'histoire s'arrête."),
        (MUTED, "Tu te réveilles dans ton lit, et tu crois ce que tu veux."),
        (RED, "La pilule rouge : tu restes au Pays des Merveilles."),
        (G, "Je te montre jusqu'où va le terrier du lapin."),
    ]
    for i, (color, line) in enumerate(quotes):
        put_centered(8 + i, line, color, cols)

    put_centered(13, "←  →   choisis   ·   R / B   ·   Entrée pour avaler", MUTED, cols)

    pill_w = 34
    gap = 8
    total = pill_w * 2 + gap
    left0 = max(2, (cols - total) // 2 + 1)
    left1 = left0 + pill_w + gap
    top = max(15, rows // 2)
    draw_pill(top, left0, "red", selected == "red")
    draw_pill(top, left1, "blue", selected == "blue")
    put_centered(rows - 2, "Remember: all I'm offering is the truth. Nothing more.", G_DIM, cols)
    flush()


def choose_pill() -> str:
    selected = "red"
    draw_choice(selected)
    while True:
        key = key_waiting(0.12)
        if key is None:
            continue
        key_l = key.lower() if len(key) == 1 else key
        if key in ("RIGHT", "LEFT") or key_l in ("a", "d", "h", "l"):
            selected = "blue" if selected == "red" else "red"
            draw_choice(selected)
        elif key_l == "r":
            selected = "red"
            draw_choice(selected)
        elif key_l == "b":
            selected = "blue"
            draw_choice(selected)
        elif key in ("\r", "\n", " "):
            return selected
        elif key in ("ESC", "q", "\x03"):
            return selected


def set_wallpaper(path: Path) -> None:
    if not path.is_file():
        return
    env = os.environ.copy()
    try:
        subprocess.run(
            ["omarchy-theme-bg-set", str(path)],
            check=False,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=8,
        )
    except Exception:
        pass


def ending(choice: str) -> None:
    rows, cols = size()
    sys.stdout.write(CLEAR)
    if choice == "red":
        flash(bg(80, 0, 0) + " ", 3)
        lines = [
            (G_BRIGHT, "Tu as choisi la pilule rouge."),
            (G, "Bienvenue dans le désert du réel."),
            (WHITE, "Welcome to the real world."),
            (G_DIM, "Chargement du fond d'écran Matrix…"),
        ]
        set_wallpaper(RED_BG)
    else:
        flash(bg(0, 20, 80) + " ", 3)
        lines = [
            (BLUE_GLOW, "Tu as choisi la pilule bleue."),
            (BLUE, "L'histoire s'arrête ici."),
            (WHITE, "You wake up in your bed…"),
            (MUTED, "Chargement du monde confortable…"),
        ]
        set_wallpaper(BLUE_BG)

    start_row = max(4, rows // 2 - 3)
    for i, (color, text) in enumerate(lines):
        typewriter(start_row + i * 2, center_col(text, cols), text, color, 0.032)
        time.sleep(0.25)
    time.sleep(1.4)


def boot_sequence() -> None:
    rows, cols = size()
    sys.stdout.write(CLEAR)
    put_centered(2, "[ SYSTÈME ]  INTRUSION DÉTECTÉE", RED, cols)
    flush()
    time.sleep(0.35)
    messages = [
        "Wake up, Neo...",
        "The Matrix has you...",
        "Follow the white rabbit.",
        "Knock, knock, Neo.",
    ]
    row = max(6, rows // 3)
    for msg in messages:
        typewriter(row, center_col(msg, cols), msg, G, 0.055)
        row += 3
        time.sleep(0.45)
    time.sleep(0.4)
    sys.stdout.write(CLEAR)
    flush()
    rain(4.6)
    sys.stdout.write(CLEAR)
    flush()
    rows, cols = size()
    typewriter(rows // 2, center_col("Connexion à la Matrix…", cols), "Connexion à la Matrix…", G, 0.04)
    time.sleep(0.7)


def main() -> int:
    atexit.register(restore)
    wait_for_fullscreen()
    setup()
    try:
        boot_sequence()
        choice = choose_pill()
        ending(choice)
    except KeyboardInterrupt:
        pass
    finally:
        restore()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
