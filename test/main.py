# pylint: disable=no-member,no-name-in-module,wrong-import-position,missing-module-docstring
import curses
from os.path import realpath
from sys import path

from typing import Callable


p = realpath("../")
print(p)
path.insert(0, p)

from lymia import const, run, Scene, on_key, Menu, MenuFormScene, Forms
from lymia.data import SceneResult, ReturnType, status
from lymia.colors import Coloring, ColorPair, color
from lymia.environment import Theme
from lymia.forms import FormFields, Text, Password
from lymia.runner import debug


class Basic(Coloring):
    """Basic color pair"""

    SELECTED = ColorPair(color.BLACK, color.YELLOW)


class MinuteClock(Scene):
    """Set an alarm (minute)"""

    def generate_time_minute(self, index: int):
        """Generate time hour by index"""
        return (
            str(index % 60),
            lambda: (
                status.set(f"Clock set: {self._time:0>2}:{index % 60:0>2}"),
                ReturnType.CONTINUE,
            )[1],
        )

    def __init__(self, time: int) -> None:
        self.margin_top = 2
        self._time = time
        super().__init__()
        self._menu: Menu[int] = Menu(
            self.generate_time_minute,
            prefix="   ",
            margin_height=(self.margin_top, 2),
            selected_style=Basic.SELECTED,
        )
        self.register_keymap(self._menu)

    def draw(self):
        self.screen.addstr(0, 0, f"Minutes (Hour selected: {self._time})")
        self._menu.draw(self.screen)
        self.show_status()

    @on_key(curses.KEY_LEFT)
    def back(self):
        """Back"""
        return ReturnType.BACK

    @on_key(curses.KEY_RIGHT)
    def exec_menu(self):
        """Pops menu and returns component"""
        comp: Callable[[], ReturnType] = self._menu.fetch()[1]  # type: ignore
        if not isinstance(comp, Forms):
            return comp()
        return ReturnType.CONTINUE

    @on_key("q")
    def quit(self):
        """On quit"""
        return ReturnType.EXIT


class Clock(Scene):
    """Set an alarm"""

    def generate_time_hour(self, index: int):
        """Generate time hour by index"""
        return str(index % 24), lambda: self.to_minute_clock(index % 24)

    def to_minute_clock(self, time: int):
        """To minute clock"""
        return MinuteClock(time)

    def __init__(self) -> None:
        self.margin_top = 2
        super().__init__()
        self._menu: Menu[MinuteClock] = Menu(
            self.generate_time_hour,
            prefix="   ",
            margin_height=(self.margin_top, 4),
            selected_style=Basic.SELECTED,
        )
        self.register_keymap(self._menu)

    def draw(self):
        self.screen.addstr(0, 0, "Hours")
        self._menu.draw(self.screen)
        self.show_status()

    @on_key(curses.KEY_LEFT)
    def back(self):
        """Back"""
        return ReturnType.BACK

    @on_key(curses.KEY_RIGHT)
    def exec_menu(self):
        """Pops menu and returns component"""
        comp: Callable[[], Scene] = self._menu.fetch()[1]  # type: ignore
        if not isinstance(comp, Forms):
            return SceneResult(comp())
        return ReturnType.CONTINUE

    @on_key("q")
    def quit(self):
        """On quit"""
        return ReturnType.EXIT


class Settings(MenuFormScene):
    """Settings component"""

    def __init__(self) -> None:
        self.margin_top = 2
        fields = FormFields(
            (Text("Username"), Password("Password")),
            self.margin_top,
        )

        menu: Menu = Menu(
            fields.to_menu_fields(),
            prefix="   ",
            margin_height=(self.margin_top, 2),
            selected_style=Basic.SELECTED,
        )
        super().__init__(menu)

    def draw(self):
        self.screen.addstr(0, 0, "App settings")
        super().draw()
        self.show_status()

    @on_key(curses.KEY_LEFT)
    def back(self):
        """Back"""
        return ReturnType.BACK

    @on_key(curses.KEY_RIGHT)
    def enter_mode(self):
        """Enter edit mode"""
        return self.select_menu_item()


class Root(Scene):
    """Root component"""

    def __init__(self) -> None:
        super().__init__()
        self._menu: Menu[ReturnType | Scene] = Menu(
            (
                ("Settings", lambda: Settings()),  # pylint: disable=unnecessary-lambda
                ("Clock", lambda: Clock()),  # pylint: disable=unnecessary-lambda
            ),
            margin_height=(2, 2),
            selected_style=Basic.SELECTED,
        )
        self.register_keymap(self._menu)

    def draw(self) -> None | ReturnType:
        self.screen.addstr(0, 0, "Hello, World!")
        self.show_status()
        self._menu.draw(self.screen)

    @on_key(curses.KEY_RIGHT)
    def exec_menu(self):
        """Pops menu and returns component"""
        comp: Callable[[], Scene] = self._menu.fetch()[1]  # type: ignore
        if not isinstance(comp, Forms):
            return SceneResult(comp())
        return ReturnType.CONTINUE

    @on_key("q")
    def quit(self):
        """On quit"""
        return ReturnType.EXIT


@debug
def init():
    """main function"""
    root = Root()
    env = Theme(const.CURSOR_HIDDEN, Basic())
    return root, env


if __name__ == "__main__":
    run(init)
