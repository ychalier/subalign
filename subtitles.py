import subprocess
import codecs
import re
import os

from subtitle import Subtitle

class Subtitles:

    def __init__(self):
        self.data = []

    def __str__(self):
        return "\n\n".join(map(str, self.data)) + "\n"

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def __iter__(self):
        return iter(self.data)

    def add(self, subtitle):
        self.data.append(subtitle)

    def save(self, filename):
        print("Saving to", filename)
        with codecs.open(filename, "w", "utf-8") as file:
            file.write(str(self))

    def from_srt(path):
        print("Loading SRT file at", path)
        subs = Subtitles()
        with codecs.open(path, "r", "utf-8") as file:
            text = file.read().replace("\r", "")
        for string in text.split("\n\n"):
            if string.strip() != "":
                subs.data.append(Subtitle.from_text(string))
        return subs

    def from_mkv(path):
        info = subprocess.Popen(["mkvinfo", path], stdout=subprocess.PIPE)
        output = info.stdout.read().decode("utf-8").split("\n")
        for i in range(len(output)):
            if "subtitles" in output[i]:
                for j in range(1, i):
                    if output[i-j].startswith("| +"):
                        track = int(re.search("(\d+)", output[i-j+1]).group(0)) - 1
                        break
                break
        print("Extracting track", track, "from MKV file into 'tmp.srt'")
        extract = subprocess.Popen(
                    ["mkvextract", "tracks", path, "{}:tmp.srt".format(track)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        extract.wait()
        subs = Subtitles.from_srt("tmp.srt")
        print("Removing 'tmp.srt'")
        os.remove("tmp.srt")
        return subs

    def from_file(path):
        if path.endswith(".srt"):
            return Subtitles.from_srt(path)
        elif path.endswith(".mkv"):
            return Subtitles.from_mkv(path)
        else:
            raise NotImplementedError("Format of '{}' not supported.".format(path))
