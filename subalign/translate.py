"""This module provides tools to translate subs from one language to another"""

import logging
import word2word  #pylint: disable=E0401


def translate(sequence, from_language, to_language):
    """Translate a WordSequence from one language to another"""
    logging.info("Translating sequence from '%s' to '%s'", from_language, to_language)
    translator = word2word.Word2word(from_language, to_language)
    new_sequence = sequence.offset(0)
    for element in new_sequence:
        try:
            element.word = " ".join(map(lambda s: s.lower(), translator(element.word)))
        except KeyError:
            pass
    return new_sequence
