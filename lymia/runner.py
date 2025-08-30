"""Generic runners"""
# pylint: disable=no-member,no-name-in-module

import curses
from functools import wraps
from typing import Callable, ParamSpec

from .data import ReturnType
from .component import Component

Ps = ParamSpec("Ps")

def runner(stdscr: curses.window, root: Component):
    """Run the whole scheme"""
    stack: list[Component] = [root]

    while stack:
        comp = stack[-1]

        if comp.should_init:
            comp.init(stdscr)

        if comp.should_clear:
            stdscr.erase()

        ret = comp.draw(stdscr)
        if ret in (ReturnType.BACK, ReturnType.ERR_BACK):
            stack.pop()
            continue

        key = stdscr.getch()
        result = comp.handle_key(key, stdscr)

        if result == ReturnType.RETURN_TO_MAIN:
            while len(stack) != 1:
                stack.pop()

        if result == ReturnType.EXIT:
            break

        if ret in (ReturnType.BACK, ReturnType.ERR_BACK):
            stack.pop()
            continue

        if isinstance(result, Component):
            stack.append(result)

def run(fn: Callable[Ps, Component]):
    """Run the app, must be used as decorator like:

    @run
    def init():
        ...
    """
    @wraps(fn)
    def inner(*args, **kwargs):
        return curses.wrapper(runner, fn(*args, **kwargs))
    return inner
