"""This modules provides tool for representing subtitles, reading and
   writting them.
"""
import re
import os
import codecs
import datetime
import logging


def parse_subrip_timecode(timecode):
    """Returns a datetime.time object from a SubRip timecode string"""
    return datetime.datetime.strptime(timecode.strip(), "%H:%M:%S,%f").time()


def format_time_to_subrip_timecode(timestamp):
    """Returns a SubRip timecode string from a datetime.time object"""
    return timestamp.strftime("%H:%M:%S") + ",%s" % timestamp.strftime("%f")[:3]


def add_delta_to_time(timestamp, delta):
    """Utility to add a datetime.timedelta object to a datetime.time one"""
    return (
        datetime.datetime.combine(datetime.date(2012, 1, 1), timestamp)
        + datetime.timedelta(seconds=delta)
    ).time()


class Subtitle:
    """A class to represent one subtitle entry."""

    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text

    def __repr__(self):
        return "Sub(%d)" % id(self)

    def __str__(self):
        return "Sub(%s, %s): %s" % (
            self.start,
            self.end,
            self.text.replace("\n", "\\n")
        )

    def shift(self, offset):
        """Create a copy with shifted times"""
        return Subtitle(
            add_delta_to_time(self.start, offset),
            add_delta_to_time(self.end, offset),
            self.text
        )

    def is_intradiegetic(self):
        """Naive check of whether the subtitle contains actual spoken text or
           only image description content.
        """
        if self.text.upper() == self.text:
            return False
        if "♪" in self.text:
            return False
        if re.match(r"^[\*\(\[^].+[\*\(\[^]$", self.text):
            return False
        return True


class SubtitleFormatter:
    """An interface for subtitle input and output"""

    def __init__(self, extension):
        self.extension = extension

    def read(self, filename, codec):
        """Read a filename and output a list of Subtitle"""
        raise NotImplementedError

    def write(self, subs, filename, codec):
        """Write a list of subtitles to a file"""
        raise NotImplementedError


class SubRipFormatter(SubtitleFormatter):
    """SubRip subtitle format. See https://en.wikipedia.org/wiki/SubRip."""

    def __init__(self):
        super(SubRipFormatter, self).__init__("srt")

    def read(self, filename, codec):
        subs = list()
        logging.debug("Reading subtitles file at %s",
                      os.path.realpath(filename))
        with codecs.open(filename, "r", codec) as file:
            buffer = {"time": "", "text": ""}
            for line in file.readlines():
                if not line.strip() and buffer["time"] and buffer["text"]:
                    timecode_start, timecode_end = buffer["time"].split("-->")
                    subs.append(Subtitle(
                        parse_subrip_timecode(timecode_start),
                        parse_subrip_timecode(timecode_end),
                        buffer["text"]
                    ))
                    buffer = {"time": "", "text": ""}
                elif re.match(r"^\d+$", line.strip()):
                    continue
                elif re.match(r"^[\d:, ]+-->[\d:, ]+$", line.strip()):
                    buffer["time"] = line.strip()
                else:
                    if buffer["text"]:
                        buffer["text"] += "\n"
                    buffer["text"] += line.strip()
        logging.debug("Loaded %s subtitles", len(subs))
        return subs

    def write(self, subs, filename, codec):
        logging.info("Writing %d subtitles to %s",
                     len(subs), os.path.realpath(filename))
        with codecs.open(filename, "w", codec) as file:
            for i, sub in enumerate(subs):
                file.write("%d\n%s --> %s\n%s\n\n" % (
                    i + 1,
                    format_time_to_subrip_timecode(sub.start),
                    format_time_to_subrip_timecode(sub.end),
                    sub.text
                ))


class SubtitleFactory:
    """Combine all formatters into a unified interface"""

    def __init__(self, codec):
        self.codec = codec
        formatters = [
            SubRipFormatter()
        ]
        self.formatters = {
            formatter.extension: formatter
            for formatter in formatters
        }

    def read(self, filename):
        """Read a filename and output a list of Subtitle"""
        extension = os.path.splitext(filename)[1][1:]
        if extension not in self.formatters:
            logging.warning(
                "No subtitles formatter found for extension '%s'", extension)
            extension = "srt"
        return self.formatters[extension].read(filename, self.codec)

    def write(self, subs, filename, extension="srt"):
        """Write a list of subtitles to a file"""
        if extension not in self.formatters:
            logging.warning(
                "No subtitles formatter found for extension '%s'", extension)
            extension = "srt"
        self.formatters[extension].write(subs, filename, self.codec)


def shift_subs(subs, offset):
    """Create a copy of subs with shifted timecodes"""
    return [sub.shift(offset) for sub in subs]
