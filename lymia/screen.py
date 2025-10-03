"""Screen"""

# pylint: disable=no-member,too-many-branches,pointless-string-statement
import curses
from typing import TypeAlias, overload

from lymia.errors import RenderError

"""
Fucking abomination, don't bother code this hell
"""


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

    @property
    def encoding(self):
        """Encoding of this screen"""
        return self._stdscr.encoding

    def _deduce_exc(self, y: int, x: int, obj_ref: str):
        content_length = len(obj_ref)
        maxy, maxx = self._stdscr.getmaxyx()
        if x + content_length >= maxx:
            return f"Content overflow for x: {x + content_length} > {maxx}"
        if y >= maxy:
            return f"Invalid height: {y} >= {maxy}"
        return "Unknown error"

    def _cook_err(self, main_msg: str, y: int, x: int, obj_ref: str, exc: curses.error):
        err = RenderError(main_msg)
        err.add_note(self._deduce_exc(y, x, obj_ref) or str(exc))
        return err

    @overload
    def add_char(self, ch: ChType, attr: int = 0):
        pass

    @overload
    def add_char(self, y: int, x: int, ch: ChType, attr: int = 0):
        pass

    def add_char(self, *args, **kwargs):
        """Paint character ch at (y, x) with attributes attr, overwriting any character previously
        painted at that location.
        By default, the character position and attributes are the
        current settings for the window object."""
        if len(args) == 1 or (len(args) == 2 and isinstance(args[1], int)):
            ch = args[0]
            attr = args[1] if len(args) == 2 else kwargs.get("attr", 0)
            x, y = kwargs.get("x", None), kwargs.get("y", None)
            if isinstance(x, int) and isinstance(y, int):
                try:
                    self._stdscr.addch(y, x, ch, attr)
                except curses.error as exc:
                    raise self._cook_err(
                        "Cannot render character", y, x, ch, exc
                    ) from None
                return
            if is_exclusively_different(x, y, int):
                raise TypeError("Inconsistent type for x and y")
            try:
                self._stdscr.addch(ch, attr)
            except curses.error as exc:
                posy, posx = self._stdscr.getyx()
                raise self._cook_err(
                    "Cannot render character", posy, posx, ch, exc
                ) from None

            return
        if len(args) >= 3:
            y, x, ch = args[:3]  # pylint: disable=unbalanced-tuple-unpacking
            attr = args[3] if len(args) > 3 else kwargs.get("attr", 0)
            try:
                self._stdscr.addch(y, x, ch, attr)
            except curses.error as exc:
                raise self._cook_err("Cannot render character", y, x, ch, exc) from None
            return
        ch = kwargs.get("ch", None)
        attr = kwargs.get("attr", 0)
        x, y = kwargs.get("x", None), kwargs.get("y", None)
        if ch is None and all((isinstance(x, int), isinstance(y, int))):
            raise ValueError("Cannot insert, passed char is None.")
        if ch is None:
            ch = args[0]  # type: ignore
        if is_exclusively_different(x, y, int):
            raise ValueError("Inconsistent type for x and y")
        if isinstance(x, int) and isinstance(y, int):
            try:
                self._stdscr.addch(x, y, ch, attr)
            except curses.error as exc:
                raise self._cook_err("Cannot render character", y, x, ch, exc) from None
            return
        try:
            self._stdscr.addch(ch, attr)
        except curses.error as exc:
            posy, posx = self._stdscr.getyx()
            raise self._cook_err(
                "Cannot render character", posy, posx, ch, exc
            ) from None
