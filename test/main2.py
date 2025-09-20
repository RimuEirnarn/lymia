"""Test 2"""

# pylint: disable=no-member,no-name-in-module,wrong-import-position,missing-module-docstring
import curses
from os.path import realpath
from sys import path


p = realpath("../")
print(p)
path.insert(0, p)

from lymia import Scene, on_key
from lymia.panel import Panel
from lymia.colors import Coloring
from lymia.data import ReturnType, status
from lymia.environment import Theme
from lymia.runner import debug, run


class Basic(Coloring):
    """Basic colors"""


def draw_character(screen: curses.window, character):
    """Draw character HUD"""
    screen.box()
    screen.addstr(1, 2, character[0])
    hp = character[1]
    mp = character[2]
    energy = character[3]
    screen.addstr(3, 3, f"HP: {hp[0]}/{hp[1]}")
    screen.addstr(4, 3, f"MP: {mp[0]}/{mp[1]}")
    screen.addstr(5, 3, f"Energy: {energy[0]}/{energy[1]}")


class Root(Scene):
    """Root component"""

    render_fps = 30

    def __init__(self) -> None:
        super().__init__()
        self._scrs: tuple[curses.window, ...]
        self._panels: tuple[Panel, ...]
        self._character = ("Rimu Aerisya Lv. 100", (8300, 8300), (75, 100), (185, 200))

    def on_unmount(self):
        for panel in self._panels:
            panel.hide()

    def draw(self) -> None:
        status.set(f"Test {self.height}x{self.width}")
        for panel in self._panels:
            panel.draw()

    def init(self, stdscr: curses.window):
        super().init(stdscr)
        self._panels = (
            Panel(
                8,
                30,
                self.height - 9,
                0,
                lambda scr: draw_character(scr, self._character),
            ),
        )
        stdscr.nodelay(True)

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


if __name__ == "__main__":
    run(init)
