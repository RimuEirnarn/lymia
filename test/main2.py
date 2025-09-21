"""Test 2"""

# pylint: disable=no-member,no-name-in-module,wrong-import-position,missing-module-docstring
import curses
from os.path import realpath
from sys import path


p = realpath("../")
path.insert(0, p)

from lymia import Scene, on_key
from lymia.anim import Animator, move_panel
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
    screen.erase()
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
    screen.erase()
    screen.box()
    menu.draw(screen)


def draw_abaction(screen: curses.window, menu: Menu):
    """Draw skill/ultimate/"""
    screen.erase()
    screen.box()
    if menu is None:
        return
    menu.draw(screen)


class Root(Scene):
    """Root component"""

    render_fps = 60
    # minimal_size = (30, 120)

    def __init__(self) -> None:
        super().__init__()
        self._panels: tuple[Panel, ...]
        self._character = ("Rimu Aerisya Lv. 100", (8300, 8300), (75, 100), (185, 200))
        self._kwdargs = {
            "prefix": " ",
            "selected_style": Basic.SELECTED,
            "margin_height": (1, 2),
            "margin_left": 1,
            "max_height": 8,
        }
        self._menu = Menu(
            (
                ("Basic Attack", lambda: "Basic Attack"),
                ("Skill", lambda: "Skill"),
                ("Ultimate", lambda: "Ultimate"),
                ("Items", lambda: "Items"),
                ("Flee", lambda: "Flee"),
            ),
            **self._kwdargs,
        )
        self._ability_menu_skill = Menu(
            (
                ("Paladin's Momentum", lambda: "Skill: Paladin's Momentum"),
                ("Reformative Catalyst", lambda: "Skill: Reformative Catalyst"),
                ("Lantern of Radiance", lambda: "Skill: Lantern of Radiance"),
                ("Skill 1", lambda: "Skill: 1"),
                ("Skill 2", lambda: "Skill: 2"),
                ("Skill 3", lambda: "Skill: 3"),
                ("Skill 4", lambda: "Skill: 4"),
            ),
            **self._kwdargs,
        )
        self._ability_menu_ultimate = Menu(
            (
                ("Vainglory's Revolution", lambda: "Ultimate: Vainglory's Revolution"),
                ("The Radiance", lambda: "Ultimate: The Radiance"),
            ),
            **self._kwdargs,
        )
        self._ability_menu_items = Menu(
            (
                ("Small HP Potion", lambda: "Items: Small HP Potion"),
                ("Medium HP Potion", lambda: "Items: Medium HP Potion"),
                ("Big HP Potion", lambda: "Items: Big HP Potion"),
            ),
            **self._kwdargs,
        )
        self._abmenu = {
            "Skill": self._ability_menu_skill,
            "Ultimate": self._ability_menu_ultimate,
            "Items": self._ability_menu_items,
        }
        self._state = {"menu": self._menu}
        self._keytype = ""
        self._target_menu = 0
        self._key = 0
        self.register_keymap(self._menu)
        self._animator: Animator = Animator(self.render_fps)

    def draw(self) -> None:
        size = f"{self.height}x{self.width}"
        k = f"Key: {self._key}"
        t = f"Menu: {self._target_menu}"
        self._animator.tick()
        self.update_panels()
        status.set(
            f"FPS: {self.fps} | Screen: {size} | {k} | {t} | Action: {self._keytype}"
        )
        self.show_status()

    def init(self, stdscr: curses.window):
        super().init(stdscr)
        self._panels = (
            Panel(*(8, 30, self.height - 9, 0), draw_character, self._character),
            Panel(*(8, 30, self.height - 9, 30), draw_action, state=self._menu),
            Panel(*(8, 30, self.height - 9, 30), draw_abaction),
        )
        self._panels[2].hide()
        stdscr.nodelay(True)

    def handle_key(self, key: int):
        # if key == 410:
        # return ReturnType.CONTINUE
        res = super().handle_key(key)
        if key != -1:
            self._key = key
        return res

    @on_key("q")
    def quit(self):
        """quit from menu"""
        return ReturnType.EXIT

    def use_panel2(self, keytype: str):
        """Use panel 2"""
        menu = self._abmenu.get(keytype, None)
        if menu is None:
            return
        self._panels[2].set_state(menu)
        anim = move_panel(
            self._panels[1], 30, self.height - 9, 60, self.height - 9, 0.5
        )
        anim.on_complete(self.panel2_oncomplete)
        self._animator.add(anim)

    def revert(self):
        """Revert to Panel 1"""
        self._panels[2].hide()
        self._panels[2].set_state(None)
        anim = move_panel(
            self._panels[1], 60, self.height - 9, 30, self.height - 9, 0.5
        )
        anim.on_complete(self.panel1_oncomplete)
        self._animator.add(anim)

    def panel1_oncomplete(self, _: Panel):
        """Panel 1 on complete"""
        self.register_keymap(self._menu)
        self._target_menu = 0

    def panel2_oncomplete(self, _: Panel):
        """Panel 2 on complete"""
        self._panels[2].show()
        menu: Menu = self._panels[2].get_state()  # type: ignore
        self.register_keymap(menu)
        self._target_menu = 1

    @on_key(curses.KEY_RIGHT)
    def select(self):
        """Select from skill menu"""
        if not self._animator.is_empty:
            return ReturnType.CONTINUE
        _, ability = (
            self._menu.fetch()
            if self._target_menu == 0
            else self._panels[2].get_state().fetch()  # type: ignore
        )
        if not isinstance(ability, Forms) and self._panels[2].panel.hidden():
            keytype = ability()
            if keytype is None:
                return ReturnType.CONTINUE
            if keytype in ("Flee", "Basic Attack"):
                self._keytype = keytype
                return ReturnType.CONTINUE
            self.use_panel2(keytype)
        if not isinstance(ability, Forms) and self._panels[2].panel.hidden() is False:
            keytype = ability()
            if keytype is None:
                return ReturnType.CONTINUE
            self._keytype = keytype
            self.revert()

        return ReturnType.CONTINUE

    @on_key(curses.KEY_LEFT)
    def unselect(self):
        """Unselect"""
        if self._panels[2].panel.hidden() is False:
            self.revert()
        return ReturnType.CONTINUE


@debug
def init():
    """init"""
    root = Root()
    env = Theme(0, Basic())
    return root, env


if __name__ == "__main__":
    run(init)
