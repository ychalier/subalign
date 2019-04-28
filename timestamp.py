def fill(int, digits=2):
    return "0" * (digits - len(str(int))) + str(int)

class Timestamp:

    def __init__(self, time=0):
        self.h = time // 3600000
        time = time % 3600000
        self.m = time // 60000
        time = time % 60000
        self.s = time // 1000
        self.ms = time % 1000

    def __str__(self):
        return "{}:{}:{},{}".format(
            fill(self.h),
            fill(self.m),
            fill(self.s),
            fill(self.ms)
        )

    def __add__(self, value):
        return Timestamp(int(self) + value)

    def __sub__(self, other):
        return int(self) - int(other)

    def __int__(self):
        return self.ms + self.s * 1000 + self.m * 60000 + self.h * 3600000

    def from_text(string):
        ts = Timestamp()
        ts.h = int(string[:2])
        ts.m = int(string[3:5])
        ts.s = int(string[6:8])
        ts.ms = int(string[9:])
        return ts
