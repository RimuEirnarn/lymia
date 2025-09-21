"""Menu (not top menu)"""

# pylint: disable=no-name-in-module,no-member

from collections.abc import Sequence
from math import inf
from os import get_terminal_size
import curses
from typing import Callable, Generic, TypeAlias, TypeVar

from lymia.colors import ColorPair
from lymia.forms import Forms

from .data import ReturnType
from .utils import prepare_windowed

T = TypeVar("T")
Fields: TypeAlias = tuple[tuple[str, Callable[[], T]], ...] | tuple[tuple[str, Forms], ...]
FieldsFn: TypeAlias = Callable[[int], tuple[str, Callable[[], T]]]


class Menu(Generic[T]):
    """Menu helper component

    fields: Menu fields, consists of label/callback
    selected_style: Style for cursor
    margin: tuple[int, int], this margin is simplified as margin top and margin bottom
    max_height: Menu's maximum height

    For fields, callback can have a `.display()` that returns a pre-rendered label data
    The content returned by `.display()` is displayed as-is.
    """

    KEYMAP_UP = curses.KEY_UP
    KEYMAP_DOWN = curses.KEY_DOWN

    def __init__(
        self,
        fields: Fields | FieldsFn,
        prefix: str = "-> ",
        selected_style: int | ColorPair = 0,
        margin_height: tuple[int, int] = (0, 0),
        margin_left: int = 0,
        max_height: int = -1,
        count: Callable[[], int] | None = None
    ) -> None:
        self._fields = fields
        self._cursor = 0
        self._selected_style = selected_style
        self._margins = margin_height
        self._max_height = max_height
        self._margin_left = margin_left
        self._prefix = prefix

        if isinstance(fields, Sequence):
            self._count_fn = lambda: len(fields)
            for _, field in fields:
                if isinstance(field, Forms):
                    field.set_prefix(self._prefix)
        else:
            self._count_fn = count if count is not None else lambda: -1

    def _get_field(self, idx: int) -> tuple[str, Callable[[], T]] | tuple[str, Forms]:
        if isinstance(self._fields, Sequence):
            return self._fields[idx]
        return self._fields(idx)

    def draw(self, stdscr: curses.window):
        """Draw menu component"""

        start, end = prepare_windowed(self._cursor, self.max_height - self._margins[1])

        for index, relative_index in enumerate(range(start, end)):
            try:
                label, content = self._get_field(relative_index)
            except (IndexError, StopIteration):
                break
            data = f"{self._prefix}{label}"
            style = 0
            if relative_index == self._cursor:
                style = curses.color_pair(int(self._selected_style))
            if hasattr(content, "display") and callable(
                getattr(content, "display", None)
            ):
                data: str = content.display()
            stdscr.addstr(self._margins[0] + index, self._margin_left, data, style)

    @property
    def max_height(self):
        """Menu max height"""
        if self._max_height == -1:
            max_height = get_terminal_size().lines
            return max_height - sum(self._margins)
        return self._max_height

    @property
    def height(self):
        """Menu height"""
        count = self._count_fn()
        if count == -1:
            return inf
        return count

    def move_down(self):
        """Move cursor down"""
        if self._cursor < self.height - 1:
            self._cursor += 1
        return ReturnType.CONTINUE

    def move_up(self):
        """Move cursor up"""
        if self._cursor > 0:
            self._cursor -= 1
        return ReturnType.CONTINUE

    def fetch(self):
        """Return callback from current cursor"""
        return self._get_field(self._cursor)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} size={self.height!r}>"
