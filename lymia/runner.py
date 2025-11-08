"""Generic runners"""

# pylint: disable=no-member,no-name-in-module

import curses
import curses.panel
from functools import wraps
from os import get_terminal_size
from selectors import DefaultSelector
import selectors
import sys
from time import sleep, perf_counter
from typing import Callable, ParamSpec

from .environment import Theme
from .data import SceneResult, ReturnType
from .scene import Scene
from .utils import hide_system

Ps = ParamSpec("Ps")
DEBUG = True


def _oob_check(sizes: tuple[int, int], minsize: tuple[int, int]):
    """Check whether current sizes is enough for minsize"""
    return not (sizes[0] < minsize[0] or sizes[1] < minsize[1])


def _oob_runner(render: curses.window, fps: int, minsize: tuple[int, int]):
    sizes = f"{minsize[0]}x{minsize[1]}"
    with hide_system(render):
        while True:
            size: tuple[int, int] = get_terminal_size()[::-1]  # type: ignore
            csize = f"{size[0]}x{size[1]}"
            print(f"Cannot go below {sizes} ({csize})", end="\r")
            if _oob_check(size, minsize):
                return
            sleep(1 / fps)


def check_resize(
    render: curses.window,
    scene: Scene,
    sizes: tuple[int, int],
    minsize: tuple[int, int],
):
    """Check scene resize"""
    new_size = render.getmaxyx()
    if sizes != new_size and scene.auto_resize:
        # scene.init(render)
        sizes = new_size
        minsize = max(scene.minimal_size, minsize)
        if sizes[0] < minsize[0] or sizes[1] < minsize[1]:
            _oob_runner(render, scene.render_fps, minsize)
        return new_size
    return sizes


def wait(render_fps: int, start: float):
    """Wait for FPS"""
    if render_fps > 1:  # why do we add this anyway?
        wend = perf_counter()
        wdt = wend - start
        frametime = 1 / render_fps
        remaining = frametime - wdt
        if remaining > 0:
            sleep(remaining)


def on_back(ret: ReturnType | None, stack: list[Scene], current: Scene):
    """On back event"""
    if ret in (ReturnType.BACK, ReturnType.ERR_BACK):
        stack.pop()
        current.on_unmount()
        return True
    return False


def screen_update():
    """Update screne"""
    curses.panel.update_panels()
    curses.doupdate()


def report_fps(scene: Scene, fc: int, end: float, start: float):
    """Report current FPS to current scene"""
    if end - start >= 1.0:
        scene.fps = fc / (end - start)
        fc = 0
        start = end
    return fc, start


def draw(scene: Scene, delta: float, start: float):
    """Draw current scene"""
    if scene.animator:
        scene.animator.deltatime = delta
    ret = scene.draw()
    screen_update()
    scene.deferred_op()
    wait(scene.render_fps, start)
    return ret


def on_exit(ret: ReturnType, stack: list[Scene]):
    """On exit"""
    if ret == ReturnType.EXIT:
        for scene in stack:
            scene.on_unmount()
        stack.clear()
        return True
    return False


def on_push(result: SceneResult, screen: curses.window, stack: list[Scene]):
    """On push"""
    if isinstance(result, SceneResult):
        scene = result.scene
        scene.init(result.target or screen)
        stack.append(scene)
        return result.target or screen
    return False


def process_scene_result(
    result: ReturnType | SceneResult,
    stack: list[Scene],
    current: Scene,
    screen: curses.window,
    root_screen: curses.window,
):
    """Process the result of handle_key and update stack/render as needed."""
    if result == ReturnType.RETURN_TO_MAIN:
        while len(stack) != 1:
            scene = stack.pop()
            scene.on_unmount()
        return screen
    if on_exit(result, stack):  # type: ignore
        return False
    if on_back(result, stack, current):  # type: ignore
        return screen
    pushed = on_push(result, root_screen, stack)  # type: ignore
    if pushed:
        return pushed
    return None


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

    if root.use_default_color:
        curses.use_default_colors()

    if env:
        env.apply()

    while stack:
        start = perf_counter()
        current = stack[-1]

        if current.should_clear:
            render.erase()

        sizes = check_resize(render, current, sizes, root_minsize)
        ret = draw(current, delta, start)

        if on_back(ret, stack, current):
            render = stdscr
            continue

        key = render.getch()
        result = current.handle_key(key)
        screen_update()

        # comp.handle_key() may mutate display
        end = perf_counter()
        delta = end - start
        frame_count += 1
        frame_count, window_start = report_fps(current, frame_count, end, window_start)

        new_render = process_scene_result(result, stack, current, render, stdscr)
        if new_render is False:
            break
        if new_render is None:
            continue
        render = new_render

    root.on_unmount()


def event_runner(
    stdscr: curses.window, root: Scene, sel: DefaultSelector, event_callback: Callable[[str, int], ReturnType], env: Theme | None = None
):
    """Run the whole stack, but with events!"""
    stdscr.nodelay(True)
    sel.register(sys.stdin, selectors.EVENT_READ, "curses")

    stack: list[Scene] = [root]
    render = stdscr
    root.init(render)
    sizes = render.getmaxyx()
    root_minsize = root.minimal_size

    if root.use_default_color:
        curses.use_default_colors()

    if env:
        env.apply()

    while stack:
        current = stack[-1]

        if current.should_clear:
            render.erase()

        sizes = check_resize(render, current, sizes, root_minsize)
        result = draw(current, 0, 0)

        if on_back(result, stack, current):
            render = stdscr
            continue

        events = sel.select()
        for key, mask in events:
            if key.data == "curses":
                ckey = render.getch()
                result = current.handle_key(ckey)
                screen_update()
            else:
                event_callback(key, mask) # type: ignore
                result = ReturnType.CONTINUE

        new_render = process_scene_result(result, stack, current, render, stdscr)  # type: ignore
        if new_render is False:
            break
        if new_render is None:
            continue
        render = new_render
    root.on_unmount()


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
    global DEBUG  # pylint: disable=global-statement
    DEBUG = True
    return fn


def run(_fn: Callable[Ps, tuple[Scene, Theme | None]], *args, **kwargs):
    """Run main function, the structure must be similiar of `@bootstrap` target function."""
    return curses.wrapper(runner, *_fn(*args, **kwargs))

def erun(_fn: Callable[Ps, tuple[Scene, DefaultSelector, Callable[[str, int], ReturnType], Theme | None]], *args, **kwargs):
    """Run the main function (event!)"""
    return curses.wrapper(event_runner, *_fn(*args, **kwargs))
