"""Curses utility"""

# pylint: disable=no-member

# from os import get_terminal_size
import curses
from contextlib import contextmanager
from typing import TypeVar

T = TypeVar("T")

@contextmanager
def hide_system(stdscr: curses.window):
    """Hide the app UI to parent TTY"""
    curses.endwin()
    try:
        yield
    finally:
        stdscr.refresh()
        curses.doupdate()

def clear_line(stdscr: curses.window, line: int):
    """Clear a line"""
    stdscr.addstr(line, 0, " " * (stdscr.getmaxyx()[1] - 1))

@contextmanager
def clear_line_yield(stdscr: curses.window, line: int):
    """Clear line through context var"""
    clear_line(stdscr, line)
    try:
        yield
    finally:
        clear_line(stdscr, line)
        stdscr.refresh()

def windowed(data: list[T] | tuple[T, ...], start: int, end: int):
    """Return an enumerated, windowed list based on start and end.
    Start/end must incorporated values returned by prepare_windowed"""
    return list(enumerate(data))[start:end]


def prepare_windowed(index: int, visible_rows: int):
    """Return min/max length for windowed function"""
    minln = max(0, index - (visible_rows // 2))
    maxln = (
        visible_rows if index <= (visible_rows // 2) else (index + visible_rows // 2)
    )
    return minln, maxln
