# pylint: disable=no-member,no-name-in-module
from os.path import realpath
from sys import path

import curses
from curses import window

p = realpath("../")
print(p)
path.insert(0,p)

from lymia import run, Component, on_key
from lymia.data import ReturnType

class Root(Component):
    """Root component"""

    def draw(self, stdscr: window) -> None | ReturnType:
        stdscr.addstr(0, 0, "Hello, World!")

    @on_key('q', 'w')
    def quit(self):
        """On quit"""
        return ReturnType.EXIT

@run
def main():
    """main function"""
    root = Root()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(0, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    return root

if __name__ == '__main__':
    main()
