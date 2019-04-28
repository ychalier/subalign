from timestamp import Timestamp

def tokenize(text):
    tokens = set()
    for word in text.replace("\n", "").split(" "):
        if word == "":
            continue
        else:
            tokens.add(word.lower())
    return tokens

class Subtitle:

    def __init__(self):
        self.id = 0
        self.start = Timestamp()
        self.stop = Timestamp()
        self.text = ""

    def __str__(self):
        text = str(self.id) + "\n"
        text += "{} --> {}\n".format(self.start, self.stop)
        text += self.text
        return text

    def sim(self, other):
        a = tokenize(self.text)
        b = tokenize(other.text)
        return float(len(a.intersection(b))) / float(len(a.union(b)))

    def from_text(string):
        subtitle = Subtitle()
        split = string.replace("\ufeff", "").split("\n")
        subtitle.id = int(split[0])
        subtitle.start = Timestamp.from_text(split[1][:12])
        subtitle.stop = Timestamp.from_text(split[1][17:29])
        subtitle.text = "\n".join(split[2:])
        return subtitle
