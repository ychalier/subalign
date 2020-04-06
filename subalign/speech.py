"""Speech-to-text utilities"""

import re
import os
import codecs
import datetime
import logging
import pocketsphinx  # pylint: disable=E0401


class TranscriptFragment:
    """Wrapper for a transcript fragment (continuous entries)"""

    HEADER = ["offset", "duration", "frames"]

    def __init__(self, offset, duration, frames, entries):
        self.offset = offset
        self.duration = duration
        self.frames = frames
        self.entries = entries

    def __iter__(self):
        return iter(self.entries)

    def from_decoder(offset, duration, decoder):  # pylint: disable=E0213
        """Build a TranscriptFragment from a Decoder"""
        fragment = TranscriptFragment(offset, duration, decoder.n_frames(), list())
        for segment in decoder.seg():
            fragment.entries.append(TranscriptEntry.from_segment(segment))
        return fragment


class TranscriptEntry:
    """Wrapper for a transcript entry"""

    HEADER = ["word", "start_frame", "end_frame",
              "prob", "ascore", "lscore", "lback"]
    FRATE = 100.

    def __init__(self, word, start_frame, end_frame,  # pylint: disable=R0913
                 prob, ascore, lscore, lback):
        self.word = word
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.prob = prob
        self.ascore = ascore
        self.lscore = lscore
        self.lback = lback

    def from_segment(segment):  # pylint: disable=E0213
        """Create a TranscriptEntry from a Segment"""
        return TranscriptEntry(
            segment.word,
            segment.start_frame,
            segment.end_frame,
            segment.prob,
            segment.ascore,
            segment.lscore,
            segment.lback
        )

    def is_tag(self):
        """Check if the entry word is a CMUSphinx transcript tag"""
        return re.match(r"^\[.+\]$", self.word) or re.match(r"^<.+>$", self.word)

    def get_word(self):
        """Clean the transcript word"""
        return re.sub(r"\(\d+\)", "", self.word)

    def start(self, fragment):
        """Return absolute entry start timecode"""
        return datetime.timedelta(
            seconds=fragment.offset + self.start_frame / TranscriptEntry.FRATE)

    def end(self, fragment):
        """Return absolute entry end timecode"""
        return datetime.timedelta(
            seconds=fragment.offset + self.end_frame / TranscriptEntry.FRATE)


class Transcript(list):
    """Audio transcript wrapper"""

    def to_list(self):
        """Return the transcript as a list of triples, filtering out non-textual
           entries.
        """
        result = list()
        for fragment, entry in self.iter_entries():
            if entry.is_tag():  # or entry.prob < -4000:
                continue
            result.append((
                entry.get_word(),
                entry.start(fragment),
                entry.end(fragment)
            ))
        return result

    def iter_entries(self):
        """Iterate over all the entries"""
        for fragment in self:
            for entry in fragment.entries:
                yield (fragment, entry)

    def save(self, filename, codec):
        """Save the transcript to a TSV file"""
        with codecs.open(filename, "w", codec) as file:
            file.write("\t".join(
                ["fragment_" + field for field in TranscriptFragment.HEADER]
                + ["segment_" + field for field in TranscriptEntry.HEADER]
            ) + "\n")
            for fragment in self:
                for entry in fragment.entries:
                    file.write("\t".join(
                        [str(getattr(fragment, field))
                         for field in TranscriptFragment.HEADER]
                        + [str(getattr(entry, field))
                           for field in TranscriptEntry.HEADER]
                    ) + "\n")

    def from_file(filename, codec):  # pylint: disable=E0213
        """Load a transcript from a TSV file"""
        transcript = Transcript()
        fhl = len(TranscriptFragment.HEADER)
        fragment = None
        with codecs.open(filename, "r", codec) as file:
            for line in file.readlines()[1:]:  # skip header
                split = line.strip().split("\t")
                fragment_bit, entry_bit = split[:fhl], split[fhl:]
                if fragment is None or fragment.offset != float(fragment_bit[0]):
                    if fragment is not None:
                        transcript.append(fragment)
                    fragment = TranscriptFragment(
                        float(fragment_bit[0]),
                        float(fragment_bit[1]),
                        int(fragment_bit[2]),
                        list()
                    )
                fragment.entries.append(TranscriptEntry(
                    entry_bit[0],
                    int(entry_bit[1]),
                    int(entry_bit[2]),
                    int(entry_bit[3]),
                    int(entry_bit[4]),
                    int(entry_bit[5]),
                    int(entry_bit[6]),
                ))
        if fragment is not None:
            transcript.append(fragment)
        return transcript


def byte_int(raw):
    """Convert bytes from WAVE header to an integer"""
    return int.from_bytes(bytearray(raw), byteorder="little", signed=True)


def configure_decoder(language):
    """Initialize a pocketsphinx Decoder with the appropriate configuration.
       TODO: Support language configuration
    """
    config = pocketsphinx.Decoder.default_config()
    model_path = os.path.join("stt", language)
    logging.debug("Loading CMUSphinx model from %s", os.path.realpath(model_path))
    config.set_string("-hmm", os.path.join(model_path, "acoustic-model"))
    config.set_string("-lm", os.path.join(model_path, "language-model.lm.bin"))
    config.set_string("-dict", os.path.join(model_path, "pronounciation-dictionary.dict"))
    config.set_string("-logfn", os.devnull)
    config.set_boolean("-remove_silence", False)
    return pocketsphinx.Decoder(config)


def speech_to_text(filename, fragment_count, fragment_duration, language):
    """Return a Transcript from an audio file"""
    logging.info(
        "Using Speech-to-text on %s (%d fragments of %ds)",
        os.path.realpath(filename),
        fragment_count,
        fragment_duration
    )
    transcript = Transcript()
    byte_rate = 16000 * 2  # sample rate * sample width
    buffer_size = 1024
    buffer = bytearray(buffer_size)
    decoder = configure_decoder(language)
    seconds_per_buffer = buffer_size / byte_rate
    with open(filename, "rb") as file:
        assert file.read(4).decode("ascii") == "RIFF"  # ChunkID
        file.seek(8)
        assert file.read(4).decode("ascii") == "WAVE"  # Format
        assert file.read(4).decode("ascii") == "fmt "  # Subchunk1ID
        assert byte_int(file.read(4)) == 16  # Subchunk1Size (PCM)
        assert byte_int(file.read(2)) == 1  # AudioFormat (PCM)
        assert byte_int(file.read(2)) == 1  # NumChannels
        assert byte_int(file.read(4)) == 16000  # SampleRate
        assert byte_int(file.read(4)) == 32000  # ByteRate
        assert byte_int(file.read(2)) == 2  # BlockAlign
        assert byte_int(file.read(2)) == 16  # BitsPerSample
        assert file.read(4).decode("ascii") == "data"  # Subchunk2ID
        bytesize = byte_int(file.read(4))  # Subchunk2Size
        for i, anchor in enumerate(range(0, bytesize, bytesize // fragment_count)):
            file.seek(anchor)
            offset_time = 0
            decoder.start_stream()
            decoder.start_utt()
            while file.readinto(buffer):
                offset_time += seconds_per_buffer
                decoder.process_raw(buffer, False, False)
                if offset_time >= fragment_duration:
                    break
            decoder.end_utt()
            transcript.append(TranscriptFragment.from_decoder(
                anchor / byte_rate,
                fragment_duration,
                decoder
            ))
            logging.debug(
                "Fragment %d/%d hypothesis: %s",
                i + 1,
                fragment_count,
                decoder.hyp().hypstr if decoder.hyp() is not None else "None"
            )
    return transcript
