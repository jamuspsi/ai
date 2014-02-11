import os
import sys
import ctypes
from ctypes import wintypes
import win32con
import win32gui
import win32api
from time import time
from handy.ice import Ice

byref = ctypes.byref
uint = ctypes.c_uint
user32 = ctypes.windll.user32

from timer import WindowsTimer
from hotkey import HotKey

from point import Point


def call(obj, name, *args, **kwargs):
    def wrap():
        getattr(obj, name)(*args, **kwargs)
    return wrap

class Wink(Ice):
    def __init__(self):
        self.init = False
        self.kill_key = win32con.VK_F6
        pass

    @property
    def cursor_location(self):
        flags, hcursor, (x,y) = win32gui.GetCursorInfo()
        return Point(x,y)

    @cursor_location.setter
    def cursor_location(self, p):
        win32api.SetCursorPos((p.x, p.y))

    def click_mouse(self, p=None):

        if p:

            x,y = p.x, p.y
            t = self.cursor_location
            #print "moving to %s" % p
            self.cursor_location = p
            p = t
        else:
            x, y = self.cursor_location.t()

        #print "Clicking at %r" % ((x,y),)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
        if p:
            pass
            self.cursor_location = p

    def setup(self):
        self.init = True

    def run(self):
        try:
            if not self.init:
                self.setup()
            self.message_pump()
        finally:
            HotKey.unregister_all()
            WindowsTimer.unregister_all()

    def message_pump(self):
        quit_key = HotKey(lambda:0, key=self.kill_key)
        msg = wintypes.MSG()
        while user32.GetMessageA (byref (msg), None, 0, 0) != 0:
            if msg.message == win32con.WM_HOTKEY:
                if msg.wParam == quit_key.id:
                    break
                HotKey.on_hotkey(msg.wParam)
            elif msg.message == win32con.WM_TIMER:
                WindowsTimer.on_WM_TIMER(msg.wParam)

            user32.TranslateMessage (byref (msg))
            user32.DispatchMessageA (byref (msg))

class C(Ice):
    pass

class AI(Wink):
    def __init__(self):
        super(AI, self).__init__()

        self.hotkeys = C()


    def setup(self):
        super(AI, self).setup()
        self.hotkeys.reload_key = HotKey(call(self, 'reload'), win32con.VK_F7)

        self.modules = {}
        from button import ButtonModule, LayoutModule

        LayoutModule(self)
        ButtonModule(self)


    def reload(self):
        from reloader import Reloader
        rl = Reloader()
        rl.reload_stuff()

