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
from lymia.menu import Menu
from lymia.colors import ColorPair, color
from lymia.forms._base import Forms


class Basic(Coloring):
    """Basic colors"""

    SELECTED = ColorPair(color.BLACK, color.WHITE)


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


def draw_action(screen: curses.window, menu: Menu):
    """Draw actions HUD"""
    screen.box()
    menu.draw(screen)


class Root(Scene):
    """Root component"""

    render_fps = 30

    def __init__(self) -> None:
        super().__init__()
        self._panels: tuple[Panel, ...]
        self._character = ("Rimu Aerisya Lv. 100", (8300, 8300), (75, 100), (185, 200))
        self._menu = Menu(
            (
                ("Basic Attack", lambda: status.set("Basic Attack")),
                ("Skill", lambda: status.set("Skill")),
                ("Ultimate", lambda: status.set("Ultimate")),
                ("Items", lambda: status.set("Items")),
                ("Flee", lambda: status.set("Flee")),
            ),
            prefix=" ",
            selected_style=Basic.SELECTED,
            margin_height=(1, 1),
            margin_left=1,
            max_height=8,
        )
        self.register_keymap(self._menu)

    def draw(self) -> None:
        self.update_panels()
        self.show_status()

    def init(self, stdscr: curses.window):
        super().init(stdscr)
        self._panels = (
            Panel(
                *(8, 30, self.height - 9, 0),
                lambda scr: draw_character(scr, self._character),
            ),
            Panel(
                *(8, 30, self.height - 9, 30), lambda scr: draw_action(scr, self._menu)
            ),
        )
        stdscr.nodelay(True)

    @on_key("q")
    def quit(self):
        """quit from menu"""
        return ReturnType.EXIT

    @on_key(curses.KEY_RIGHT)
    def select(self):
        """Select from skill menu"""
        _, ability = self._menu.fetch()
        if not isinstance(ability, Forms):
            ability()
        return ReturnType.OK

@debug
def init():
    """init"""
    root = Root()
    env = Theme(0, Basic())
    return root, env


if __name__ == "__main__":
    run(init)
