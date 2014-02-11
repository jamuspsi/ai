import ctypes
from ctypes import wintypes
import win32con
import win32gui
from time import time
from handy.ice import Ice

byref = ctypes.byref
uint = ctypes.c_uint
user32 = ctypes.windll.user32

try:
    old_registry = WindowsTimer.registry
except:
    pass


class WindowsTimer(object):
    registry = {}

    def __init__(self, function, ms, register=True):
        self.id = None

        self.ms = ms
        self.function = function

        self.last_time = None

        self.registered = False

        if register:
            self.register()

    def _tick(self):
        now = time()
        if self.last_time is not None:
            elapsed = now - self.last_time
        else:
            elapsed = self.ms / 1000.0

        self.last_time = now

        self.tick(elapsed)

    def tick(self, elapsed):
        if self.function:
            self.function(elapsed=elapsed)

    def register(self):
        print self.ms
        self.id = user32.SetTimer(None, 0, uint(self.ms), 0)
        WindowsTimer.registry[self.id] = self

        self.last_time = time()
        self.registered = True

    def unregister(self):
        user32.KillTimer(None, self.id)
        del WindowsTimer.registry[self.id]
        self.last_time = None
        self.registered = False

    @staticmethod
    def unregister_all():
        for timer in WindowsTimer.registry.values():
            timer.unregister()

    @staticmethod
    def on_WM_TIMER(id):
        timer = WindowsTimer.registry.get(id)
        if timer:
            timer._tick()


try:
    WindowsTimer.registry = old_registry
except:
    pass

