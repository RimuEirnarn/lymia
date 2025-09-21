"""Component base class module"""

# pylint: disable=no-member,unused-import,unused-argument
from inspect import signature
import curses
from os import get_terminal_size, terminal_size
from typing import Callable, Self, TypeAlias, TypeGuard, TypeVar

from lymia.anim import Animator
from lymia.panel import Panel

from .utils import clear_line
from .data import ReturnType, status, SceneResult
from .menu import Menu
from .forms import Forms

Tcomp = TypeVar("Tcomp", bound="Scene")

DefaultCallback: TypeAlias = "Callable[[], ReturnType | SceneResult]"
WinCallback: TypeAlias = "Callable[[curses.window], ReturnType]"
DefaultMethod: TypeAlias = "Callable[[Tcomp], ReturnType | SceneResult]"
WinMethod: TypeAlias = "Callable[[Tcomp, curses.window], ReturnType]"

GenericFunction: TypeAlias = "DefaultCallback | WinCallback"
Method: TypeAlias = "DefaultMethod | WinMethod"
Function: TypeAlias = "GenericFunction | Method"


def uses_window(fn: Function) -> "TypeGuard[WinCallback | WinMethod]":
    """Check if a function uses a window param"""
    fn_signature = signature(fn)
    return "stdscr" in fn_signature.parameters


def is_method(fn: Function) -> TypeGuard[Method]:
    """Check if a function uses 'Self'"""
    fn_signature = signature(fn)
    return "self" in fn_signature.parameters

def is_method_and_uses_window(fn: Function) -> TypeGuard[WinMethod]:
    """Check if a function is a method and uses window param"""
    return uses_window(fn) and is_method(fn)

def no_op():
    """No op"""
    return ReturnType.CONTINUE


class SceneMeta(type):
    """Scene metaclass"""

    def __new__(mcs, name, bases, dct: dict):
        keymap = {}
        actions = {}
        for fn in dct.values():
            if hasattr(fn, "_keys"):
                for key in fn._keys:
                    key: int = ord(key) if isinstance(key, str) else key
                    keymap[key] = fn.__name__
                actions[fn.__name__] = fn
        dct["_keymap"] = keymap
        dct["_actions"] = actions
        return super().__new__(mcs, name, bases, dct)


class Scene(metaclass=SceneMeta):
    """Base class for all sorts of scenes"""

    generic_height: int = 3
    reserved_lines: int = 5
    should_clear: bool = True
    auto_resize: bool = True
    render_fps = -1

    _keymap: dict[int, str] = {}
    _actions: "dict[str, DefaultCallback | WinCallback]" = {}


    def __init__(self) -> None:
        self._init = False
        self._override = False
        self._screen: curses.window = None # type: ignore
        self._panels: tuple[Panel, ...] = ()
        self._animator: Animator

    def draw(self) -> None | ReturnType:
        """Draw this component"""
        raise NotImplementedError

    def keymap_override(self, key: int) -> ReturnType:
        """Override key component"""
        return ReturnType.REVERT_OVERRIDE

    def handle_key(self, key: int) -> "ReturnType | SceneResult":
        """Handle key component"""
        if self._override:
            ret = self.keymap_override(key)
            if ret == ReturnType.REVERT_OVERRIDE:
                self._override = False
                return ReturnType.CONTINUE
            return ret
        name = self._keymap.get(key, None)
        if not name:
            return ReturnType.CONTINUE

        action = self._actions.get(name, no_op)
        if action is no_op:
            return ReturnType.CONTINUE
        if is_method(action):
            if is_method_and_uses_window(action):
                return action(self, self._screen)
            return action(self) # type: ignore
        if uses_window(action):
            return action(self._screen) # type: ignore
        return action()  # type: ignore

    def show_status(self):
        """Show statuses"""
        height = self.height
        stdscr = self._screen
        try:
            clear_line(stdscr, height - 1)
            stdscr.addstr(height - 1, 0, status.get())
        except curses.error: # occurs during resize
            pass

    def update_panels(self):
        """Update all panels"""
        for panel in self._panels:
            panel.draw()

    def syscall(self) -> ReturnType:
        """Do whatever you want."""
        return ReturnType.OK

    def leave(self):
        """Leave this component"""
        return ReturnType.BACK

    def init(self, stdscr: curses.window):
        """Initialize this component"""
        if self._init is True:
            return
        self._screen = stdscr
        self._init = True

    def on_unmount(self):
        """On unmount"""
        for panel in self._panels:
            panel.hide()
        return None

    def register_keymap(self, menu: Menu):
        """Register a menu's keymap into this component"""
        key_up = menu.KEYMAP_UP
        key_down = menu.KEYMAP_DOWN
        call_up = menu.move_up
        call_down = menu.move_down
        self._keymap[key_up] = "move_up"
        self._keymap[key_down] = "move_down"
        self._actions['move_up'] = call_up
        self._actions['move_down'] = call_down

    @property
    def term_size(self): # type: ignore
        """Return terminal size"""
        if self.auto_resize:
            return get_terminal_size()
        y, x = self.screen.getmaxyx()
        return terminal_size((x, y))

    @property
    def height(self):
        """Height of current terminal"""
        return self.term_size.lines

    @property
    def width(self):
        """Width of current terminal"""
        return self.term_size.columns

    @property
    def unreserved_lines(self):
        """Return unreserved lines"""
        return self.height - self.reserved_lines

    @property
    def screen(self):
        """This compoenent's painter"""
        if self._screen is None:
            raise RuntimeError("This component has not initialized yet")
        return self._screen

    @property
    def animator(self):
        """Component's animator"""
        if not hasattr(self, '_animator'):
            return None
        return self._animator

    def __repr__(self) -> str:
        return f"<Component/{type(self).__name__}>"

class MenuFormScene(Scene):
    """Base for components with menu and forms"""

    def __init__(self, menu: Menu):
        super().__init__()
        self._menu = menu
        self._active_form: Forms | None = None
        self.register_keymap(menu)

    def draw(self):
        self._menu.draw(self._screen)
        if self._active_form:
            self._active_form.draw(self._screen)

    def keymap_override(self, key: int) -> ReturnType:
        if self._active_form:
            ret = self._active_form.handle_edit(key)
            if ret == ReturnType.REVERT_OVERRIDE:
                self._active_form = None
            return ret
        return ReturnType.REVERT_OVERRIDE

    def select_menu_item(self):
        """Select menu item"""
        _, item = self._menu.fetch()
        if isinstance(item, Forms):
            item()
            self._active_form = item
            self._override = True
            return ReturnType.OVERRIDE
        return ReturnType.CONTINUE

def on_key(*keys: str | int):
    """On key event binding"""

    def inner(fn: "Function"):
        fn._keys = keys  # pylint: disable=protected-access
        return fn

    return inner
