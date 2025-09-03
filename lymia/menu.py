"""Menu (not top menu)"""

# pylint: disable=no-name-in-module,no-member

from os import get_terminal_size
import curses
from typing import Callable, Generic, TypeAlias, TypeVar

from .data import ReturnType
from .utils import prepare_windowed, windowed

T = TypeVar("T")
Fields: TypeAlias = tuple[tuple[str, Callable[[T], None]], ...]


class Menu(Generic[T]):
    """Menu helper component

    fields: Menu fields, consists of label/callback
    selected_style: Style for cursor
    margin: tuple[int, int], this margin is simplified as margin top and margin bottom
    max_height: Menu's maximum height

    For fields, callback can have a `.display()` that returns a pre-rendered label data
    The content returned by `.display()` is displayed as-is.
    """

    def __init__(
        self,
        fields: Fields[T],
        prefix: str = "-> ",
        selected_style: int = 0,
        margin: tuple[int, int] = (0, 0),
        max_height: int = -1,
    ) -> None:
        self._fields = fields
        self._cursor = 0
        self._selected_style = selected_style
        self._margins = margin
        self._max_height = max_height
        self._prefix = prefix

    def draw(self, stdscr: curses.window):
        """Draw menu component"""

        start, end = prepare_windowed(self._cursor, self.max_height)

        for index, (relative_index, (label, content)) in enumerate(
            windowed(self._fields, start, end)
        ):
            data = f"{self._prefix}{label}"
            style = 0
            if relative_index == self._cursor:
                style = curses.color_pair(self._selected_style)
            if hasattr(content, "display") and callable(
                getattr(content, "display", None)
            ):
                data: str = content.display()
            stdscr.addstr(self._margins[0] + index, 0, data, style)

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
        return len(self._fields)

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

    def fetch(self) -> tuple[str, Callable[[T], None]]:
        """Return callback from current cursor"""
        return self._fields[self._cursor]
