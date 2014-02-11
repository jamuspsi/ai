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
    old_registry = HotKey.registry
    old_next_id = HotKey.next_id
except:
    pass

class HotKey(Ice):
    next_id = 1
    registry = {}

    def __init__(self, function, key, mod=0, register=True):
        self.id = HotKey.next_id
        HotKey.next_id += 1
        self.function = function
        self.key = key
        self.mod = mod

        if register:
            self.register()

    def register(self):
        if not user32.RegisterHotKey(None, self.id, self.mod, self.key):
            print "Unable to register id %s" % self.id
            #hotkey_functions[hotkey_counter] = self.function

        HotKey.registry[self.id] = self

    def unregister(self):
        user32.UnregisterHotKey (None, self.id)
        del HotKey.registry[self.id]

    @staticmethod
    def unregister_all():
        for hk in HotKey.registry.values():
            hk.unregister()

    @staticmethod
    def on_hotkey(id):
        hk = HotKey.registry.get(id)
        if hk:
            hk.fire()

    def fire(self):
        if self.function:
            self.function()





try:
    HotKey.registry = old_registry
    HotKey.next_id = old_next_id
except:
    pass
