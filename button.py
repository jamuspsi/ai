from handy.ice import Ice
from hotkey import HotKey
from timer import WindowsTimer
import win32con
import ImageGrab
from datetime import datetime

from point import Point


def call(obj, name, *args, **kwargs):
    def wrap(*discarded, **discarded2):
        getattr(obj, name)(*args, **kwargs)
    return wrap

class Module(Ice):
    def __init__(self, wink):
        super(Module, self).__init__()
        self.wink = wink
        self.wink.modules[self.__class__.__name__] = self
        self.layout = self.wink.modules['LayoutModule']
        self.hotkeys = []
        self.timers = []

        self.activated = False

    def toggle_module(self, tog=None):
        if tog is None:
            tog = not self.activated

        if self.activated and not tog:
            self.deactivate()
        elif not self.activated and tog:
            self.activate()

    def activate(self):
        self.activated = True
        pass
    def deactivate(self):
        self.activated = False
        pass

    @property
    def cursor_location(self):
        return self.wink.cursor_location

    @cursor_location.setter
    def cursor_location(self, p):
        self.wink.cursor_location = p

    def click_mouse(self, *args, **kwargs):
        return self.wink.click_mouse(*args, **kwargs)

    def move_rel(self, point):
        self.cursor_location = self.layout.to_absolute(point)

    def click_rel(self, point):
        self.click_mouse(self.layout.to_absolute(point))




class ButtonModule(Module):
    def __init__(self, *args, **kwargs):
        super(ButtonModule, self).__init__(*args, **kwargs)
        self.perfect_clicks = 0
        self.purples = 100
        self.last_plant_time = datetime.min


        self.toggle_button = HotKey(call(self, 'toggle_module'), win32con.VK_F8)
        self.button_timer = WindowsTimer(call(self, 'find_and_click'), 250, register=False)

    def activate(self):
        self.button_timer.register()
        super(ButtonModule, self).activate()

    def deactivate(self):
        self.button_timer.unregister()
        super(ButtonModule, self).deactivate()


    def find_button(self, elapsed=0, pix=None):
        #print "Trying to find the button."
        here = self.cursor_location

        if not pix:
            screen_offset = here.plus(-300, -200)
            bbox = (here.x-300, here.y-200, here.x+300, here.y+200)
            ss = ImageGrab.grab(bbox)

            #print "Got image: %r" % ss

            pix = ss.load()
        else:
            screen_offset = Point(*self.layout.main_bbox[:2])

        grab_size = Point(600, 400)
        localhere = grab_size.center()

        def is_in_circle(p):
            if p.x < 0 or p.y < 0 or p.x >= grab_size.x or p.y >= grab_size.y:
                return False

            c = pix[p.t()]

            if c[0] > 0 and c[1] == c[2] == 0:
                return False

            answer =  not (c[0] == c[1] == c[2] and c[0] >= 15) and p.x < grab_size.x and p.y < grab_size.y and p.x > 0 and p.y > 0
            if not answer:
                pass
                #print "Stopping at ", c
            return answer
            return pix[p.t()] == (200, 100, 0)

        reference_point = localhere.copy()
        color = pix[reference_point.t()]
        for l in xrange(3):
            # Search left and right from the previous point
            # until it stops being 200, 100, 0
            # Left:
            min_x = max_x = reference_point.x
            min_y = max_y = reference_point.y

            p = reference_point.copy()
            while is_in_circle(p):
                min_x = p.x
                p.x -= 1

            # Right:
            p.x = max_x
            while is_in_circle(p):
                max_x = p.x
                p.x += 1

            p.x = int(round((max_x - min_x +0) / 2.0)) + min_x
            # Up
            while is_in_circle(p):
                min_y = p.y
                p.y -= 1

            p.y = max_y
            while is_in_circle(p):
                max_y = p.y
                p.y += 1

            p.y = int(round((max_y - min_y +0) / 2.0, 0)) + min_y
            reference_point = p
            #print "Hmm. ", (min_x, max_x, min_y, max_y)
            #print "Got closer: ", p.t()


        center_point = reference_point.plus(screen_offset.x, screen_offset.y)

        return center_point

    def find_and_click(self):
        if not self.layout.analyzed:
            self.layout.analyze()

        pix = self.layout.get_main_pix()
        self.repair_point = Point(94809, 317362)
        repair_color = pix.at_rel(self.repair_point)
        repair_abs = self.layout.to_absolute(self.repair_point)

        #print "Repair color is %r" % (repair_color,)
        #print "Repair button is at rel %s, abs %s" % (self.repair_point, repair_abs)

        if repair_color == (151, 100, 229):
            print "Clicking repair!"
            self.click_mouse(self.layout.to_absolute(self.repair_point))
            return


        center_point = self.find_button(pix)
        #print "The center is at ", center_point.t()
        print "Clicking the button at %s" % center_point
        if self.perfect_clicks >= 10:
            center_point = center_point.plus(3, 0)
            self.perfect_clicks = 0
        else:
            self.perfect_clicks += 1
            self.purples += 1
        self.cursor_location = center_point
        self.click_mouse()

        if self.purples >= 100:
            shop_point = Point(91815, 251494)
            boost_point = Point(393210, 51895)
            charge_point = Point(453090, 113771)

            print "Clicking some shop buttons."
            self.click_mouse(self.layout.to_absolute(shop_point))
            self.click_mouse(self.layout.to_absolute(boost_point))
            self.click_mouse(self.layout.to_absolute(charge_point))
            self.click_mouse(self.layout.to_absolute(shop_point))
            #self.click(self.layout.to_absolute)
            self.purples -= 100

        # Can I kill ants?
        green_point = Point(536921, 439118)

        if pix.at_rel(green_point) == (75, 162, 11):
            print "Green ant kill"
            self.click_mouse(self.layout.to_absolute(green_point))

        red_point = Point(595803, 443110)
        if pix.at_rel(red_point) == (168, 36, 36):
            print "Red ant kill"
            self.click_mouse(self.layout.to_absolute(red_point))

        # Can I refill the battery?
        battery_point = Point(132733, 485026)
        if pix.at_rel(battery_point) != (255, 0, 255):
            print "Charging battery"
            self.click_mouse(self.layout.to_absolute(battery_point))

        # Can I harvest trees?
        harvest_point = Point(22953, 484028)
        if pix.at_rel(harvest_point) != (68, 31, 25):
            print "Harvesting trees"
            self.click_mouse(self.layout.to_absolute(harvest_point))

        # should I plant trees?
        if (datetime.now()-self.last_plant_time).total_seconds() >= 301:
            self.last_plant_time = datetime.now()
            t = self.cursor_location
            from time import sleep
            world_location = Point(454088, 8981)
            garden_location = Point(455086, 111775)

            print "Switching to garden"
            self.move_rel(world_location)
            sleep(0.25)
            self.click_rel(garden_location)
            print "Switched"

            print "Clicking gray seed."
            grey_location = Point(18961, 326344)
            self.click_rel(grey_location)

            print "Clicking plant all"
            plant_location = Point(316364, 325346)
            self.click_rel(plant_location)

            print "Switching to button"
            self.move_rel(world_location)
            sleep(0.25)
            button_location = Point(446104, 163671)
            self.click_rel(button_location)
            print "Switched"

            self.move_rel(Point(247503, 142713))
            #self.cursor_location = t




class LayoutModule(Module):
    def __init__(self, *args, **kwargs):
        super(LayoutModule, self).__init__(*args, **kwargs)
        self.hk_analyze = HotKey(call(self, 'analyze'), win32con.VK_F9)
        self.hk_inspect = HotKey(call(self, 'inspect'), win32con.VK_F10)
        self.analyzed = False
        self.main_bbox = None
        self.prev_inspect = None

    def analyze(self):
        button_point = self.wink.modules['ButtonModule'].find_button()

        # Search left and right for 51, then for non51.
        ss = ImageGrab.grab()
        pix = ss.load()
        self.screen_size = Point(*ss.size)

        left_edge = button_point.x
        y = button_point.y

        all_same = lambda c: c[0] == c[1] == c[2]
        # until grey
        while left_edge >= 0:
            left_edge -= 1
            if pix[left_edge, y] == (51,51,51):
                break
        while left_edge >= 0:
            left_edge -= 1
            if not all_same(pix[left_edge, y]):
                left_edge += 1
                break

        right_edge = button_point.x
        while right_edge < self.screen_size.x-1:
            right_edge += 1
            if pix[right_edge, y] == (51,51,51):
                break
        while right_edge < self.screen_size.x-1:
            right_edge += 1
            if not all_same(pix[right_edge, y]):
                right_edge -= 1
                break

        self.left_edge = left_edge
        self.right_edge = right_edge

        # Next, search up and down from the left side.
        top_edge = y
        while top_edge >= 0:
            top_edge -= 1
            if pix[left_edge, top_edge] != (51,51,51):
                top_edge += 1
                break

        bottom_edge = y
        while bottom_edge < self.screen_size.y-1:
            bottom_edge += 1
            if pix[left_edge, bottom_edge] != (51, 51, 51):
                bottom_edge -= 1
                break

        self.top_edge = top_edge
        self.bottom_edge = bottom_edge

        self.main_bbox = (self.left_edge, self.top_edge, self.right_edge, self.bottom_edge)
        print "Found main bbox: %r" % (self.main_bbox,)

        self.scale = 1000 * (707.0-209) / (self.main_bbox[2] - self.main_bbox[0] * 1.0)
        print "Found scale is: %r" % self.scale

        self.rel_point = Point(self.left_edge, self.top_edge)
        print "Rel point is: %r" % self.rel_point

        print "Analyzed."
        self.analyzed = True

    def inspect(self):
        pointer = self.cursor_location
        bbox = (pointer.x, pointer.y, pointer.x+1, pointer.y+1)
        ss = ImageGrab.grab(bbox)
        pix = ss.load()

        print "At %s, color is %r" % (pointer, pix[0,0])
        if self.main_bbox:
            # Find the relative point of this.
            relative = self.to_relative(pointer)
            reversed = self.to_absolute(relative)
            print "  Relative: %s  Reversed: %s" % (relative, reversed)

        prev = self.prev_inspect
        if prev:
            pss = ImageGrab.grab((prev.x, prev.y, prev.x+1, prev.y+1))
            ppix = pss.load()
            print "Previous spot %s is now %r" % (self.prev_inspect, ppix[0,0])
            if self.main_bbox:
                # Find the relative point of this.
                relative = self.to_relative(prev)
                reversed = self.to_absolute(relative)
                print "  Relative: %s  Reversed: %s" % (relative, reversed)

        self.prev_inspect = pointer


    def to_relative(self, point):
        # This is important.
        # Multiply an absolute by this to get relative pixels.
        #bbox = self.main_bbox
        #scale = 1000 * (707.0-209) / (bbox[2] - bbox[0] * 1.0)
        # Point should be inside the bbox.
        relative_to_box = point.plus(self.rel_point.neg())
        scaled = Point(int(relative_to_box.x * self.scale),
                       int(relative_to_box.y * self.scale))

        return scaled

    def to_absolute(self, point):
        #bbox = self.main_bbox
        #scale = 1000 * (707.0-209) / (bbox[2] - bbox[0] * 1.0)
        relative_to_box = Point(int(round(point.x / self.scale)),
                                int(round(point.y / self.scale)))
        absolute = relative_to_box.plus(self.rel_point)
        return absolute

    def get_main_pix(self):
        img = ImageGrab.grab()
        return PixWrapper(img, self)

class PixWrapper(Ice):
    def __init__(self, ss, layout):
        self.pix = ss.load()
        self.width = ss.size[0]
        self.height = ss.size[0]
        self.layout = layout


    def at_rel(self, point):
        absolute = self.layout.to_absolute(point)

        return self[absolute]

    def __getitem__(self, x, y=None):
        if type(x) is Point:
            y = x.y
            x = x.x
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return (0,0,0)
        else:
            return self.pix[x,y]








