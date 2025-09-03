"""Constants"""

import curses

SPECIAL_KEYS: tuple[int] = tuple(
    (value for key, value in curses.__dict__.items() if key.startswith("KEY"))
)
KEY_ESC = 27
KEY_ENTER = 10
KEY_BACKSPACE = 127

CURSOR_HIDDEN = 0
CURSOR_VISIBLE = 1
CURSOR_BLOCK = 2
