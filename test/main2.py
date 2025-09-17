"""Test 2"""

# pylint: disable=no-member,no-name-in-module,wrong-import-position,missing-module-docstring
import curses
from curses.panel import new_panel, panel, update_panels
from os.path import realpath
from sys import path


p = realpath("../")
print(p)
path.insert(0, p)

from lymia import Component, on_key
from lymia.colors import Coloring
from lymia.data import ReturnType, status
from lymia.environment import Theme
from lymia.runner import debug, run

class Basic(Coloring):
    """Basic colors"""

class Root(Component):
    """Root component"""
    def __init__(self) -> None:
        super().__init__()
        self._panel: panel
        self._scr: curses.window

    def on_unmount(self):
        self._panel.hide()

    def draw(self) -> None:
        status.set("Test")
        # self._panel.addstr(0, 0, "something?") # type: ignore
        self._scr.box()
        self._scr.addstr(1, 1, "Hello from Panel 1")
        update_panels()
        self.show_status()

    def init(self, stdscr: curses.window):
        super().init(stdscr)
        self._scr = curses.newwin(7, 40, 3, 35)
        self._panel = new_panel(self._scr)

    @on_key("q")
    def quit(self):
        """quit from menu"""
        return ReturnType.EXIT

@debug
def init():
    """init"""
    root = Root()
    env = Theme(0, Basic())
    return root, env

if __name__ == '__main__':
    run(init)
