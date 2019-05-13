from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re

from timestamp import Timestamp

stemmer = PorterStemmer()

class Subtitle:

    def __init__(self):
        self.id = 0
        self.start = Timestamp()
        self.stop = Timestamp()
        self.text = ""
        self.clean_text = ""

    def __str__(self):
        text = str(self.id) + "\n"
        text += "{} --> {}\n".format(self.start, self.stop)
        text += self.text
        text += "\n"
        return text

    def clean(self):
        text = re.sub("<.*?>", "", self.text)
        text = re.sub("[A-Z ]+:", "", text)
        text = re.sub("\(.*?\)", "", text)
        text = re.sub("\[.*?\]", "", text)
        self.clean_text = text.lower()

    def tokenize(self):
        self.clean()
        return [
            stemmer.stem(token)
            for token in word_tokenize(self.clean_text)
            if token not in list(",.!?;:") + ["..."]
        ]

    def from_text(string):
        subtitle = Subtitle()
        split = string.replace("\ufeff", "").split("\n")
        subtitle.id = int(split[0])
        subtitle.start = Timestamp.from_text(split[1][:12])
        subtitle.stop = Timestamp.from_text(split[1][17:29])
        subtitle.text = "\n".join(split[2:])
        return subtitle
