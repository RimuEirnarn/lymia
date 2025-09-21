"""Animation"""

from typing import Callable
from .panel import Panel

class Animator:
    """Animator"""
    def __init__(self, fps: int):
        if fps <= 0:
            raise ValueError(f"Invalid FPS target: {fps}")
        self.fps = fps
        self._dt = 1 / fps
        self.animations: "list[BaseAnim]" = []

    def add(self, animation: "BaseAnim"):
        """Add animations"""
        self.animations.append(animation)

    @property
    def deltatime(self):
        """Delta time"""
        return self._dt

    @deltatime.setter
    def deltatime(self, dt: float):
        """delta time"""
        self._dt = dt

    def tick(self):
        """Tick"""
        dt = self.deltatime

        for anim in self.animations[:]:
            anim.update(dt)
            if anim.finished:
                self.animations.remove(anim)

class BaseAnim:
    """Base class for all animation"""
    def __init__(self) -> None:
        self._finished = False
        self._target: Panel
        self._callback: Callable[[Panel], None] = lambda panel: panel.show()

    def on_complete(self, callback: Callable[[Panel], None]):
        """On complete callback"""
        self._callback = callback

    @property
    def finished(self):
        """Is finished"""
        return self._finished

    def update(self, dt: float):
        """Update"""
        raise NotImplementedError

class Animation(BaseAnim):
    """Animation handler"""
    def __init__(self, target: Panel, duration: int | float, update_fn: Callable[[Panel, float], None]):
        super().__init__()
        self._target = target
        self._duration = duration
        self._update_fn = update_fn
        self._elapsed = 0

    def update(self, dt: int):
        """Update"""
        if self._finished:
            return
        self._elapsed += dt
        t = min(self._elapsed / self._duration, 1.0)  # normalized progress
        self._update_fn(self._target, t)
        if self._elapsed >= self._duration:
            self._finished = True
            self._callback(self._target)


class KeyframeAnimation(BaseAnim):
    """Keyframe animation"""
    def __init__(
        self,
        target: Panel,
        keyframes: list[tuple[int, tuple[int, int]]],
        duration: int | float,
        interp_fn: Callable[[int, int, float], float] | None = None,
    ):
        super().__init__()
        self._target = target
        self._keyframes = sorted(keyframes, key=lambda k: k[0])
        self._duration = duration
        self._elapsed = 0
        self._interp_fn = interp_fn or self.linear

    def linear(self, a, b, t):
        """Linear changes"""
        return a + (b - a) * t

    def update(self, dt: float):
        """Update"""
        if self.finished:
            return
        self._elapsed += dt
        progress = min(self._elapsed / self._duration, 1.0)

        # find current keyframe segment
        for i in range(len(self._keyframes) - 1):
            t1, v1 = self._keyframes[i]
            t2, v2 = self._keyframes[i + 1]
            if t1 <= progress <= t2:
                local_t = (progress - t1) / (t2 - t1)
                x = self._interp_fn(v1[0], v2[0], local_t)
                y = self._interp_fn(v1[1], v2[1], local_t)
                self._target.move(int(y), int(x))
                break

        if progress >= 1.0:
            self._finished = True
            self._callback(self._target)

def move_panel(panel: Panel, x1: int, y1: int, x2: int, y2: int, duration: int | float):
    """Move panels around"""
    def updater(target: Panel, t: float):
        x = int(x1 + (x2 - x1) * t)
        y = int(y1 + (y2 - y1) * t)
        target.move(x, y)
    return Animation(panel, duration, updater)
