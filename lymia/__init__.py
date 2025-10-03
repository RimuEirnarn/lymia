"""Lymia"""

from .progress import Progress
from .panel import Panel
from .anim import Animation, Animator, KeyframeAnimation
from .runner import bootstrap, run
from .menu import Menu, HorizontalMenu
from .scene import Scene, MenuFormScene, on_key
from .data import status, ReturnInfo, ReturnType
from .utils import hide_system, clear_line, clear_line_yield
from .forms import Password, Text, FormFields, Forms

__lymia_debug__ = True
__version__ = "0.0.4"
__all__ = [
    'bootstrap',
    'run',
    'Scene',
    'on_key',
    'status',
    "status",
    "ReturnInfo",
    "ReturnType",
    "hide_system",
    "clear_line",
    "clear_line_yield",
    "Menu",
    "MenuFormScene",
    "Password",
    "Text",
    'FormFields',
    "Forms",
    "Animator",
    "Animation",
    'KeyframeAnimation',
    'Panel',
    'Progress',
    'HorizontalMenu'
]

if __lymia_debug__:
    print("Ehe~")
