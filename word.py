class Word:

    def __init__(self, wid=0, lb=0, up=0, txt="", src=0):
        self.id = wid
        self.lower_bound = lb
        self.upper_bound = up
        self.text = txt
        self.source = src

    def __repr__(self):
        return "{}. {}".format(self.id, self.text)

    def __str__(self):
        return self.text
