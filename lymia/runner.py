"""Generic runners"""
# pylint: disable=no-member,no-name-in-module

import curses
import curses.panel
from functools import wraps
from time import sleep, perf_counter
from typing import Callable, ParamSpec

from .environment import Theme
from .data import SceneResult, ReturnType
from .scene import Scene

Ps = ParamSpec("Ps")
DEBUG = True

def runner(stdscr: curses.window, root: Scene, env: Theme | None = None):
    """Run the whole scheme"""
    stack: list[Scene] = [root]
    render = stdscr
    root.init(render)
    sizes = render.getmaxyx()
    root_minsize = root.minimal_size
    delta: float = 0
    start = end = 0
    frame_count = 0
    window_start = perf_counter()
    remaining = 0
    wdt = 0
    wend = 0

    if env:
        env.apply()

    while stack:
        start = perf_counter()

        comp = stack[-1]

        if comp.should_clear:
            render.erase()

        new_size = render.getmaxyx()
        if sizes != new_size and comp.auto_resize:
            comp.init(render)
            sizes = new_size

        if root_minsize != (-1, -1):
            if sizes[0] < root_minsize[0] or sizes[1] < root_minsize[1]:
                size = f"{root_minsize[0]}x{root_minsize[1]}"
                raise RuntimeError(f"Cannot go lower below {size} ({sizes})")

        if comp.animator:
            comp.animator.deltatime = delta
        ret = comp.draw()
        curses.panel.update_panels()
        curses.doupdate()
        if comp.render_fps > 1: # why do we add this anyway?
            wend = perf_counter()
            wdt = wend - start
            frametime = 1 / comp.render_fps
            remaining = frametime - wdt
            if remaining > 0:
                sleep(remaining)
            # comp.fps = 1 / delta

        # curses.panel.update_panels()
        if ret in (ReturnType.BACK, ReturnType.ERR_BACK):
            stack.pop()
            comp.on_unmount()
            render = stdscr
            continue

        key = render.getch()
        result = comp.handle_key(key)
        curses.panel.update_panels()
        curses.doupdate()

        # if DEBUG:
            # status.set(f"{comp!r}: {result!r}")
            # comp.show_status(stdscr)

        if result == ReturnType.RETURN_TO_MAIN:
            render = stdscr
            while len(stack) != 1:
                scene = stack.pop()
                scene.on_unmount()

        # comp.handle_key() may mutate display
        end = perf_counter()
        delta = end - start
        frame_count += 1
        if end - window_start >= 1.0:
            comp.fps = frame_count / (end - window_start)
            frame_count = 0
            window_start = end

        if result == ReturnType.EXIT:
            for scene in stack:
                scene.on_unmount()
            stack.clear()
            break

        if result in (ReturnType.BACK, ReturnType.ERR_BACK):
            stack.pop()
            comp.on_unmount()
            render = stdscr
            continue

        if isinstance(result, SceneResult):
            scene = result.scene
            render = result.target or stdscr
            scene.init(render)
            stack.append(scene)

def bootstrap(fn: Callable[Ps, tuple[Scene, Theme | None]]):
    """Run the app, must be used as decorator like:

    @bootstrap
    def init():
        ...
    """
    @wraps(fn)
    def inner(*args, **kwargs):
        return curses.wrapper(runner, *fn(*args, **kwargs))
    return inner

def debug(fn: Callable[Ps, tuple[Scene, Theme | None]]):
    """Enable debug mode"""
    global DEBUG # pylint: disable=global-statement
    DEBUG = True
    return fn

def run(_fn: Callable[Ps, tuple[Scene, Theme | None]], *args, **kwargs):
    """Run main function, the structure must be similiar of `@bootstrap` target function."""
    return curses.wrapper(runner, *_fn(*args, **kwargs))
