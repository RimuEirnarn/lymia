"""Menu (not top menu)"""

# pylint: disable=no-name-in-module,no-member

from collections.abc import Sequence
from math import inf
import curses
from typing import Any, Callable, Generic, TypeAlias, TypeVar

from lymia.colors import ColorPair
from lymia.forms import Forms

from .data import ReturnType
from .utils import prepare_windowed

T = TypeVar("T")
Fields: TypeAlias = (
    tuple[tuple[str, Callable[[], T]], ...] | tuple[tuple[str, Forms], ...]
)
FieldsFn: TypeAlias = Callable[[int], tuple[str, Callable[[], T]]]

class MenuEntry:
    """Menu entry"""
    def __init__(self, label: str | Callable[[], str], content: Any = None, *,
                 prefix: str = "",
                 suffix: str = "",
                 style: int | None = None,
                 preselected_style: int | None = None,
                 extra: dict | None = None):
        self._label = label
        self._content = content
        self._prefix = prefix
        self._suffix = suffix
        self._style = style
        self._preselected_style = preselected_style
        self.extra = extra or {}

    @property
    def content(self):
        """Content"""
        return self._content

    def display(self) -> str:
        """Display"""
        if callable(self._label):
            text = self._label()
        else:
            text = self._label
        return f"{self._prefix}{text}{self._suffix}"

    def get_style(self, selected: bool) -> int:
        """Get style"""
        if selected and self._preselected_style is not None:
            return self._preselected_style
        return self._style or 0


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
        suffix: str = "",
        selected_style: int | ColorPair = 0,
        margin_height: tuple[int, int] = (0, 0),
        margin_left: int = 0,
        max_height: int = -1,
        count: Callable[[], int] | None = None,
    ) -> None:
        self._fields = fields
        self._cursor = 0
        self._selected_style = selected_style
        self._margins = margin_height
        self._max_height = max_height
        self._last_maxheight = max_height
        self._margin_left = margin_left
        self._prefix = prefix
        self._suffix = suffix

        if isinstance(fields, Sequence):
            self._count_fn = lambda: len(fields)
            for _, field in fields:
                if isinstance(field, Forms):
                    field.set_prefix(self._prefix)
        else:
            self._count_fn = count if count is not None else lambda: -1

    def _get_field(self, idx: int) -> MenuEntry:
        raw = self._fields[idx] if isinstance(self._fields, Sequence) else self._fields(idx)

        if isinstance(raw, MenuEntry):
            return raw  # already normalized

        if isinstance(raw, tuple) and len(raw) == 2:
            label, content = raw
            if isinstance(content, Forms):
                return MenuEntry(content.display(), content)
            return MenuEntry(label, content, prefix=self._prefix, suffix=self._suffix)

        return MenuEntry(str(raw), prefix=self._prefix)

    def draw(self, stdscr: curses.window):
        """Draw menu component"""

        maxh, _ = stdscr.getmaxyx()
        self._last_maxheight = maxh

        start, end = prepare_windowed(self._cursor, maxh - self._margins[1])

        for index, relative_index in enumerate(range(start, end)):
            try:
                entry = self._get_field(relative_index)
            except (IndexError, StopIteration):
                break
            data = entry.display()
            # with hide_system(stdscr):
                # style = curses.color_pair(int(self._selected_style) \
                    # if relative_index == self._cursor else entry.get_style(False))
                # print(style, entry._style)
                # input()
            style = curses.color_pair(int(self._selected_style) \
                    if relative_index == self._cursor else entry.get_style(False))

            stdscr.addstr(self._margins[0] + index, self._margin_left, data, style)

    def get_keymap(self) -> dict[str, tuple[int, Callable[[], ReturnType]]]:
        """Get instance keymap"""
        return {
            "move_up": (self.KEYMAP_UP, self.move_up),
            "move_down": (self.KEYMAP_DOWN, self.move_down),
        }

    @property
    def max_height(self):
        """Menu max height"""
        if self._max_height == -1:
            max_height = self._last_maxheight
            return max(max_height - sum(self._margins), -1)
        return self._max_height

    @property
    def height(self):
        """Menu height"""
        count = self._count_fn()
        if count == -1:
            return inf
        return count

    @property
    def cursor(self):
        """Return this menu's cursor"""
        return self._cursor

    def reset_cursor(self):
        """Reset cursor"""
        self._cursor = 0

    def seek(self, cursor: int):
        """Seek to cursor"""
        if cursor < 0:
            return
        if cursor <= self.height - 1:
            self._cursor = cursor

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


class HorizontalMenu(Menu):
    """Horizontal Menu"""

    KEYMAP_LEFT = curses.KEY_LEFT
    KEYMAP_RIGHT = curses.KEY_RIGHT

    def __init__(
        self,
        fields: Fields | FieldsFn,
        prefix: str = "",
        suffix: str = "",
        selected_style: int | ColorPair = 0,
        margin_height: tuple[int, int] = (0, 0),
        margin_left: int = 0,
        max_width: int = -1,
        count: Callable[[], int] | None = None,
    ) -> None:
        super().__init__(
            fields,
            prefix,
            suffix,
            selected_style,
            margin_height,
            margin_left,
            -1,
            count,
        )
        self._scroll_x = 0
        self._max_width = max_width

        # lazy field fetcher
    def _make_str(self, idx: int):
        entry  = self._get_field(idx)
        return entry.display()

    def _tell_style(self, idx: int):
        return self._get_field(idx).get_style

    def draw(self, stdscr: curses.window) -> None:
        _, max_x = stdscr.getmaxyx()
        y = self._margins[0]
        viewport_left = self._margin_left
        viewport_width = max_x - viewport_left
        if viewport_width <= 0:
            return

        if not hasattr(self, "_scroll_x"):
            self._scroll_x = 0



        # --- compute cursor string width ---
        try:
            cursor_str = self._make_str(self._cursor)
        except (IndexError, StopIteration):
            return
        cursor_start = sum(len(self._make_str(i)) + 1 for i in range(self._cursor))
        cursor_end = cursor_start + len(cursor_str)

        # --- adjust _scroll_x to keep cursor visible ---
        if cursor_end - self._scroll_x > viewport_width:
            self._scroll_x = cursor_end - viewport_width
        if cursor_start - self._scroll_x < 0:
            self._scroll_x = cursor_start

        # --- draw items from index 0 until viewport right ---
        menu_x = 0
        i = 0
        gap = 1
        while True:
            try:
                s = self._make_str(i)
            except (IndexError, StopIteration):
                break
            item_start = menu_x
            item_end = menu_x + len(s)
            menu_x += len(s) + gap

            # completely outside viewport? skip
            if item_end <= self._scroll_x:
                i += 1
                continue
            if item_start >= self._scroll_x + viewport_width:
                break

            # visible part intersection
            visible_start = max(item_start, self._scroll_x)
            visible_end = min(item_end, self._scroll_x + viewport_width)
            start_in_s = visible_start - item_start
            length = visible_end - visible_start
            screen_x = visible_start - self._scroll_x + viewport_left

            default = self._tell_style(i)(False)
            style = curses.color_pair(int(self._selected_style) \
                                      if i == self._cursor else default)
            substr = s[start_in_s : start_in_s + length]
            stdscr.addnstr(y, screen_x, substr, length, style)

            i += 1

    def get_keymap(self) -> dict[str, tuple[int, Callable[[], ReturnType]]]:
        return {
            "move_left": (self.KEYMAP_LEFT, self.move_up),
            "move_right": (self.KEYMAP_RIGHT, self.move_down),
        }
