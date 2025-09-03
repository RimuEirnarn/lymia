# pylint: disable=no-member,no-name-in-module,wrong-import-position,missing-module-docstring
from os.path import realpath
from sys import path

from curses import window

from lymia.forms import FormFields

p = realpath("../")
print(p)
path.insert(0,p)

from lymia import const, run, Component, on_key
from lymia.data import ReturnType
from lymia.menu import Menu
from lymia.colors import Coloring, ColorPair, color
from lymia.environment import Theme

class Basic(Coloring):
    """Basic color pair"""
    SELECTED = ColorPair(color.BLACK, color.YELLOW)

class Settings(Component):
    """Settings component"""

    def __init__(self) -> None:
        super().__init__()
        self.margin_top = 2
        self._fields = FormFields((), self.margin_top)
        self._menu = Menu(self._fields.to_menu_fields(), prefix="   ", margin=(self.margin_top, 2))

    def draw(self, stdscr: window) -> None | ReturnType:
        stdscr.addstr(0, 0, "App settings")
        self._menu.draw(stdscr)

class Root(Component):
    """Root component"""

    def draw(self, stdscr: window) -> None | ReturnType:
        stdscr.addstr(0, 0, "Hello, World!")

    @on_key('q', 'w')
    def quit(self):
        """On quit"""
        return ReturnType.EXIT

def init():
    """main function"""
    root = Root()
    env = Theme(const.CURSOR_HIDDEN, Basic())
    return root, env

if __name__ == '__main__':
    run(init)
