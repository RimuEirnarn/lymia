"""Screen"""

# pylint: disable=no-member

import curses
from typing import TypeAlias, overload

ChType: TypeAlias = str | bytes | int

def is_exclusively_different(a, b, type_):
    """Is a/b exclusively different?"""
    if isinstance(a, type_) and not isinstance(b, type_):
        return True
    if isinstance(b, type_) and not isinstance(a, type_):
        return True
    return False

class Screen:
    """High level screen impl"""

    def __init__(self, backend: curses.window) -> None:
        self._stdscr = backend

    @overload
    def add_char(self, ch: ChType, attr: int = 0):
        pass

    @overload
    def add_char(self, y: int, x: int, ch: ChType, attr: int = 0):
        pass

    def add_char(self, *args, **kwargs):
        """Adds a character to the screen"""
        if len(args) == 1 or (len(args) == 2 and isinstance(args[1], int)):
            ch = args[0]
            attr = args[1] if len(args) == 2 else kwargs.get("attr", 0)
            x, y = kwargs.get("x", None), kwargs.get("y", None)
            if isinstance(x, int) and isinstance(y, int):
                self._stdscr.addch(y, x, ch, attr)
                return
            if is_exclusively_different(x, y, int):
                raise TypeError("Inconsistent type for x and y")
            self._stdscr.addch(ch, attr)
            return
        if len(args) >= 3:
            y, x, ch = args[:3]  # pylint: disable=unbalanced-tuple-unpacking
            attr = args[3] if len(args) > 3 else kwargs.get("attr", 0)
            self._stdscr.addch(y, x, ch, attr)
            return
        ch = kwargs.get("ch", None)
        attr = kwargs.get("attr", 0)
        x, y = kwargs.get("x", None), kwargs.get("y", None)
        if ch is None and all((isinstance(x, int), isinstance(y, int))):
            raise ValueError("Cannot insert, passed char is None.")
        if ch is None:
            ch = args[0] # type: ignore
        if is_exclusively_different(x, y, int):
            raise ValueError("Inconsistent type for x and y")
        if isinstance(x, int) and isinstance(y, int):
            self._stdscr.addch(x, y, ch, attr)
            return
        self._stdscr.addch(ch, attr)
