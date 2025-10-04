"""Forms base class"""

# pylint: disable=no-name-in-module,no-member,unused-argument,too-many-instance-attributes

import curses
from typing import Any

from ..data import ReturnType
from .. import const


class Forms:
    """Base class for all sorts of forms"""

    LEFT_KEYS = (curses.KEY_LEFT,)
    RIGHT_KEYS = (curses.KEY_RIGHT,)

    def __init__(
        self,
        label: str,
        value: Any = None,
        suffix: str = ": ",
        margin_left: int = 0,
        field_pos: int = 0,
        style: int = 0,
    ) -> None:
        self._buffer = value
        self._label = label
        self._label_suffix = suffix
        self._margin_left = margin_left
        self._field_height_pos = field_pos
        self._style = style
        self._cursor = 0
        self._editing = False
        self._escdelay = curses.get_escdelay()
        self._prefix = ""

    @property
    def label(self):
        """Field label"""
        return self._label

    @property
    def editing(self):
        """If current field is in edit mode"""
        return self._editing

    @property
    def value(self):
        """Value of current field"""
        return self._buffer

    @value.setter
    def value(self, v: str):
        """Value of current field"""
        self._buffer = v

    @property
    def displayed_value(self):
        """Displayed value of current field"""
        return self._buffer

    def display(self):
        """Returns pre-rendered of combination of label, suffix, and displayed value"""
        if not self._editing:
            return (
                f"{self._prefix}{self.label}{self._label_suffix}{self.displayed_value}"
            )
        return ""

    def __call__(self) -> None:
        self.enter_edit()

    def set_field_pos(self, num: int):
        """Set field position"""
        self._field_height_pos = num
        return self

    def set_prefix(self, prefix: str):
        """Set prefix"""
        self._prefix = prefix
        return self

    def reposition_cursor(self, stdscr: curses.window, prefix: int):
        """Reposition cursor"""
        stdscr.move(self._field_height_pos, prefix + self._cursor)

    def draw(self, stdscr: curses.window):
        """Draw this form"""
        content = (
            f"{self._prefix}{self._label}{self._label_suffix}{self.displayed_value}"
        )
        cursor_prefix = len(self._prefix) + len(self._label) + len(self._label_suffix)
        stdscr.addstr(self._field_height_pos, 0, content)
        if self._editing:
            self.reposition_cursor(stdscr, cursor_prefix)

    def enter_edit(self):
        """Enter edit mode"""
        curses.set_escdelay(1)
        curses.curs_set(2)
        self._editing = True
        self._cursor = len(self._buffer)

    def exit_edit(self):
        """Exit edit mode"""
        curses.set_escdelay(self._escdelay)
        curses.curs_set(0)
        self._editing = False

    def validate(self, char: str):
        """Validate current value"""
        return True

    def handle_edit(self, key: int):
        """Handle key edit"""
        if key in (curses.KEY_BACKSPACE, const.KEY_BACKSPACE):
            self._buffer = self._buffer[:-1]
            if self._cursor > 0:
                self._cursor -= 1
            return ReturnType.CONTINUE

        if key in self.LEFT_KEYS and self._cursor > 0:
            self._cursor -= 1
        if key in self.RIGHT_KEYS and self._cursor < len(self._buffer):
            self._cursor += 1

        if key in (curses.KEY_ENTER, const.KEY_ENTER):
            self.exit_edit()
            return ReturnType.REVERT_OVERRIDE

        if key == const.KEY_ESC:
            self._buffer = ""
            self.exit_edit()
            return ReturnType.REVERT_OVERRIDE

        if key in const.SPECIAL_KEYS:
            return ReturnType.CONTINUE
        char = chr(key)

        if not self.validate(char):
            return ReturnType.ERR

        if self._cursor != len(self._buffer):  # <-- Not at the end?
            self._buffer = (
                self._buffer[: self._cursor] + char + self._buffer[self._cursor :]
            )
            self._cursor += 1
            return ReturnType.CONTINUE
        self._buffer += char
        self._cursor += 1
        return ReturnType.CONTINUE

    def __repr__(self) -> str:
        return f"<Forms/{type(self).__name__}>"
