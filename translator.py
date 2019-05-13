import copy
import json
import time

from googletrans import Translator
from subtitles import Subtitles

def translate(subs, src, dest):
    print("Translating from", src, "to", dest)
    new_subs = Subtitles()
    translator = Translator()
    for i, sub in enumerate(subs.data):
        time.sleep(1)
        print("\r{}/{}".format(i, len(subs.data)), end="")
        new_sub = copy.deepcopy(sub)
        new_sub.text = translator.translate(sub.text, src=src, dest=dest).text
        new_subs.add(new_sub)
    return new_subs
