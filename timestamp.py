def padd(base, filler="0", count=2):
    return filler * (count - len(str(base))) + str(base)

class Timestamp:

    def __init__(self, time=0):
        self.set(time)

    def set(self, time):
        time = int(time)
        self.h = time // 3600000
        time = time % 3600000
        self.m = time // 60000
        time = time % 60000
        self.s = time // 1000
        self.ms = time % 1000

    def __str__(self):
        return "{}:{}:{},{}".format(
            padd(self.h),
            padd(self.m),
            padd(self.s),
            padd(self.ms, count=3)
        )

    def __add__(self, value):
        return Timestamp(int(self) + int(value))

    def __sub__(self, other):
        return int(self) - int(other)

    def __int__(self):
        return self.ms + self.s * 1000 + self.m * 60000 + self.h * 3600000

    def sync(self, intercept, slope):
        self.set((1 - slope) * int(self) - intercept)

    def from_text(string):
        ts = Timestamp()
        ts.h = int(string[:2])
        ts.m = int(string[3:5])
        ts.s = int(string[6:8])
        ts.ms = int(string[9:])
        return ts
