from handy.ice import Ice


class Point(Ice):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def t(self):
        return self.x, self.y

    def plus(self, x, y=None):
        if type(x) is Point and y is None:
            return Point(self.x + x.x, self.y+x.y)
        return Point(self.x+x, self.y+y)

    def neg(self):
        return Point(-1 * self.x, -1 * self.y)

    def center(self):
        return Point(int(self.x/2), int(self.y/2))

    def copy(self):
        return Point(self.x, self.y)

    def __str__(self):
        return '<%d, %d>' % (self.x, self.y)