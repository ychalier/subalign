"""This modules provides tools to align target subs on reference subs"""
import codecs
import datetime
import math
import logging
import re
import nltk  # pylint: disable=E0401


def time_to_timedelta(timeobj):
    """Convert a datetime.time object into datetime.timedelta"""
    return datetime.timedelta(
        hours=timeobj.hour,
        minutes=timeobj.minute,
        seconds=timeobj.second,
        microseconds=int(timeobj.strftime("%f"))
    )


class WordSequenceElement:
    """A word with an associated timeframe"""

    def __init__(self, word, start_time, end_time):
        self.word = word
        self.start_time = start_time
        self.end_time = end_time

    def __str__(self):
        return "WSE<%s (%s-%s)>" % (self.word, self.start_time, self.end_time)

    def __eq__(self, other):
        return self.word == other.word

    def format(self, delimiter="\t"):
        """Serialize a WordSequenceElement"""
        return delimiter.join([
            self.word,
            str(self.start_time.total_seconds()),
            str(self.end_time.total_seconds()),
        ])


class WordSequence(list):
    """List of WordSequenceElement"""

    def iter_groups(self, min_start=None, max_end=None):
        """Iterates over elements, grouping together elements with same
           start_time and end_time attributes.
        """
        buffer = [[], None, None]
        for element in self:
            if (buffer[1] is not None and
                    (buffer[1] != element.start_time or buffer[2] != element.end_time)):
                if ((min_start is None or buffer[1].total_seconds() >= min_start)
                        and (max_end is None or buffer[2].total_seconds() < max_end)):
                    yield (
                        " ".join(buffer[0]),
                        buffer[1].total_seconds(),
                        buffer[2].total_seconds()
                    )
                buffer = [[], None, None]
            buffer[0].append(element.word)
            buffer[1] = element.start_time
            buffer[2] = element.end_time
        if (len(buffer[0]) > 0
                and (min_start is None or buffer[1].total_seconds() >= min_start)
                and (max_end is None or buffer[2].total_seconds() < max_end)):
            yield (" ".join(buffer[0]), buffer[1].total_seconds(), buffer[2].total_seconds())

    def offset(self, amount):
        """Return a new WordSequence with shifted elements"""
        sequence = WordSequence()
        for element in self:
            sequence.append(WordSequenceElement(
                element.word,
                element.start_time + datetime.timedelta(seconds=amount),
                element.end_time + datetime.timedelta(seconds=amount)
            ))
        return sequence

    def svg(self, other, filename, **options):
        """Draw a SVG object comparing two word sequences"""
        options.setdefault("padding", .2)
        # options.setdefault("step", .1)
        options.setdefault("sup_step", 1)
        options.setdefault("min_start", None)
        options.setdefault("max_end", None)

        boundaries = [0, 0]
        if options["min_start"] is None:
            boundaries[0] = min(self.start(), other.start()).total_seconds()\
                - options["padding"]
        else:
            boundaries[0] = max(
                options["min_start"],
                min(self.start(), other.start()).total_seconds()
            ) - options["padding"]
        if options["max_end"] is None:
            boundaries[1] = max(self.end(), other.end()).total_seconds()\
                + options["padding"]
        else:
            boundaries[1] = min(
                options["max_end"],
                max(self.end(), other.end()).total_seconds()
            ) + options["padding"]
        view_box = (boundaries[0], -1.5, boundaries[1] - boundaries[0], 3)
        svg_core = ""

        # Plot background
        svg_core += '<rect x="%f" y="%f" width="%f" height="%f" fill="white" />' % view_box

        # Plot grid and axis
        svg_core += "".join(map(lambda s: s.strip(), ("""
        <defs>
            <pattern id="small_grid" width=".1" height=".1" patternUnits="userSpaceOnUse">
                <path d="M 0 0 L 0 0 0 .1" fill="none" stroke="gray" stroke-width=".002"/>
            </pattern>
            <pattern id="grid" width="1" height="1" patternUnits="userSpaceOnUse">
                <rect width="1" height="1" fill="url(#small_grid)"/>
                <path d="M 0 0 L 0 0 0 1" fill="none" stroke="gray" stroke-width=".02"/>
            </pattern>
        </defs>
        <rect x="%f" y="%f" width="%f" height="%f" fill="url(#grid)" />
        """.split("\n")))) % view_box
        svg_core += '<line stroke="black" stroke-width=".01" x1="%f" y1="%f" x2="%f" y2="%f" />'\
            % (boundaries[0], 0, boundaries[1], 0)
        svg_core += '<g font-family="Segoe UI" font-size=".09" text-anchor="middle" >'
        for i in range(
                int(boundaries[0] / options["sup_step"]),
                int(boundaries[1] / options["sup_step"])):
            svg_core += '<text x="%.2f" y=".12">%s</text>'\
                % (i * options["sup_step"], datetime.timedelta(seconds=i * options["sup_step"]))
        svg_core += '</g>'

        # Plot rectangles
        svg_core += '<g fill="#4c72b0" stroke="black" stroke-width="0.005">'
        for _, start, end in self.iter_groups(options["min_start"], options["max_end"]):
            svg_core += '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" />'\
                % (start, -1.3, end - start, 1)
        svg_core += "</g>"
        svg_core += '<g fill="#dd8452" stroke="black" stroke-width="0.005">'
        for _, start, end in other.iter_groups(options["min_start"], options["max_end"]):
            svg_core += '<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" />'\
                % (start, .3, end - start, 1)
        svg_core += "</g>"

        # Plot texts
        svg_core += '<g font-family="Segoe UI" font-size=".1" text-anchor="middle" fill="black">'
        for i, (text, start, end) in\
            enumerate(self.iter_groups(options["min_start"], options["max_end"])):
            svg_core += '<text x="%.3f" y="%.3f">%s</text>'\
                % (.5 * (start + end), -.6 - .4 * (i % 2), text)
        for i, (text, start, end) in\
            enumerate(other.iter_groups(options["min_start"], options["max_end"])):
            svg_core += '<text x="%.3f" y="%.3f">%s</text>'\
                % (.5 * (start + end), .6 + .4 * (i % 2), text)
        svg_core += "</g>"

        template = "".join((
            '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEW_BOX}">',
            '{SVG_CORE}',
            '</svg>'
        ))
        with codecs.open(filename, "w", "utf8") as file:
            file.write(template.format(
                SVG_CORE=svg_core.strip(),
                VIEW_BOX="%f %f %f %f" % view_box
            ).strip())

    def from_list(elements):  # pylint: disable=E0213
        """Build a WordSequence from a list of triples of the form
           (word, start_time, end_time)
        """
        sequence = WordSequence()
        for element in elements:
            sequence.append(WordSequenceElement(*element))
        return sequence

    def from_file(filename, codec):  # pylint: disable=E0213
        """Load a WordSequence from a .tsv file"""
        sequence = WordSequence()
        with codecs.open(filename, "r", codec) as file:
            for line in file.readlines():
                if line.strip() == "":
                    continue
                split = line.strip().split("\t")
                if len(split) != 3:
                    continue
                word, start_time, end_time = split
                sequence.append(WordSequenceElement(
                    word.strip(),
                    datetime.timedelta(seconds=float(start_time.strip())),
                    datetime.timedelta(seconds=float(end_time.strip())),
                ))
        return sequence

    def from_subs(subs, language, keep_subs):  # pylint: disable=E0213
        """Build a WordSequence from a list of Subtitle"""
        sequence = WordSequence()
        for sub in subs:
            if not sub.is_intradiegetic():
                continue
            tokens = [
                re.sub(r"\W+", " ", token).strip()
                for token in nltk.tokenize.word_tokenize(sub.text, language=language)
                if token not in ",.;:/\\\"#()[]-_{}$%*?!'`"
            ]
            duration = time_to_timedelta(sub.end) - time_to_timedelta(sub.start)
            total_chars = sum(map(len, tokens))
            current_offset = datetime.timedelta(seconds=0)
            for token in tokens:
                if keep_subs:
                    sequence.append(WordSequenceElement(
                        token,
                        time_to_timedelta(sub.start),
                        time_to_timedelta(sub.end),
                    ))
                else:
                    token_duration = len(token) / total_chars * duration
                    sequence.append(WordSequenceElement(
                        token,
                        time_to_timedelta(sub.start) + current_offset,
                        time_to_timedelta(sub.start) + current_offset + token_duration,
                    ))
                    current_offset += token_duration
        return sequence

    def save(self, filename, codec):
        """Write the sequence to a .tsv file"""
        with codecs.open(filename, "w", codec) as file:
            for element in self:
                file.write("%s\n" % element.format())

    def start(self):
        """Return the first time index of the sequence"""
        return self[0].start_time

    def end(self):
        """Return the last time index of the sequence"""
        return self[-1].end_time

    def duration(self):
        """Return duration of the sequence"""
        return self.end() - self.start()

    def find_offset(self, other, lang, default_max_iters, similarity_measure_key):
        """Find a constant offset to apply to the target to align it on the
           reference.
        """
        logging.info("Finding offset between two sequences")
        encoder = WordEncoder(lang)
        total_offset = 0
        previous_width = None
        for width in [5, 2, 1, .5, .2, .1, .05, .02, .01]:
            max_iters = default_max_iters
            if previous_width is not None:
                max_iters = 2 * math.ceil(previous_width / width) + 1
            bucket = WordBucketSequence(encoder, self, width, 0)
            target_bucket = WordBucketSequence(encoder, other, width, total_offset)
            offset, _ = bucket.find_offset(
                target_bucket,
                max_iters,
                SIMILARITY_MEASURE_INDEX[similarity_measure_key]
            )
            total_offset -= offset * width
            previous_width = width
            logging.debug(
                "Alignment of width %.2fs found for offset %d (total: %.2f; sim: %d)",
                width,
                offset,
                total_offset,
                bucket.similarity(
                    target_bucket,
                    offset,
                    overlap_count
                ) * len(bucket)
            )
        return total_offset


class WordEncoder:
    """Map words to integers for faster comparison"""

    def __init__(self, language):
        self.stopwords = frozenset(nltk.corpus.stopwords.words(language))
        self.stemmer = nltk.stem.snowball.SnowballStemmer(language)
        self.counter = 0
        self.index = dict()  # dict of {word: number}
        self.lemmas = dict()  # dict of {word: lemma}

    def encode(self, word):
        """Return the integer encoding of a word"""
        if " " in word:
            numbers = list()
            for sub_word in word.split(" "):
                lemma = self.lemmatize(sub_word)
                number = self.index.get(lemma)
                if number is not None:
                    numbers.append(number)
            if len(numbers) > 0:
                target_number = numbers[0]
            else:
                target_number = self.counter
                self.counter += 1
            for sub_word in word.split(" "):
                lemma = self.lemmatize(sub_word)
                self.index[lemma] = target_number
            return target_number
        lemma = self.lemmatize(word)
        if lemma is None:
            return None
        number = self.index.get(lemma)
        if number is None:
            number = self.counter
            self.counter += 1
            self.index[lemma] = number
            self.index[number] = lemma
        return number

    def lemmatize(self, word):
        """Return the cannonic form a word, to relax the incoming strict matching"""
        lemma = self.lemmas.get(word)
        if lemma is None and word.lower() not in self.stopwords:
            lemma = self.stemmer.stem(word.lower())
            self.lemmas[word] = lemma
        return lemma



class WordBucketSequence(dict):
    """A dictionnary to discretize timed and during elements into buckets.
       Keys are bucket ids (integers), and values are frozensets of elements
       belonging to the corresponding bucket.
    """

    def __init__(self, encoder, sequence, width, shift):
        super(WordBucketSequence, self).__init__()
        self.width = width
        self.shift = shift
        for bucket_id in range(self.hash(sequence.start()),
                               self.hash(sequence.end()) + 1):
            self[bucket_id] = set()
        for element in sequence:
            for bucket_id in range(self.hash(element.start_time),
                                   self.hash(element.end_time) + 1):
                encoding = encoder.encode(element.word)
                if encoding is not None:
                    self[bucket_id].add(encoding)
        for bucket_id in list(self.keys()):
            if len(self[bucket_id]) == 0:
                del self[bucket_id]
            else:
                self[bucket_id] = frozenset(self[bucket_id])

    def hash(self, timecode):
        """Take a timedelta object and return a bucket id"""
        return math.floor((timecode.total_seconds() + self.shift) / self.width)

    def similarity(self, other, offset, measure):
        """Compute the mean similarity measure between two bucket sequences"""
        return sum(
            measure(self[bucket_id], other.get(bucket_id + offset, []))
            for bucket_id in self
        ) / len(self)

    def find_offset(self, other, max_iters, similarity_measure):
        """Find the best offset to align two WordBucketSequence"""
        maximum_index, maximum_value = None, None
        for i in range(1, max_iters + 1):
            offset = (-1) ** i * (i // 2)
            similarity = self.similarity(other, offset, similarity_measure)
            if maximum_value is None or similarity > maximum_value:
                maximum_value = similarity
                maximum_index = offset
        return maximum_index, maximum_value


def jaccard_index(bucket_a, bucket_b):
    """https://en.wikipedia.org/wiki/Jaccard_index"""
    return len(bucket_a.intersection(bucket_b)) / len(bucket_a.union(bucket_b))


def overlap_coefficient(bucket_a, bucket_b):
    """https://en.wikipedia.org/wiki/Overlap_coefficient"""
    return len(bucket_a.intersection(bucket_b))\
        / max(1, min(len(bucket_a), len(bucket_b)))


def overlap_count(bucket_a, bucket_b):
    """Simplest similarity measure"""
    return len(bucket_a.intersection(bucket_b))


SIMILARITY_MEASURE_INDEX = {
    "jaccard-index": jaccard_index,
    "overlap-coeff": overlap_coefficient,
    "overlap-count": overlap_count
}
