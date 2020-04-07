"""Tests for subalign.translate"""

import unittest
import datetime
import subalign.sequence
import subalign.translate


class TranslateTest(unittest.TestCase):

    """Test case for subalign.translate module"""

    def setUp(self):
        dtd = datetime.timedelta()
        self.word_sequence = subalign.sequence.WordSequence.from_list([
            ("hello", dtd, dtd),
            ("my", dtd, dtd),
            ("name", dtd, dtd),
            ("odskfjoisdjf", dtd, dtd),
        ])

    def test_length(self):
        """Check if the returned length is alright"""
        seq = subalign.translate.translate(self.word_sequence, "en", "fr")
        self.assertEqual(len(self.word_sequence), len(seq))

    def test_correctness(self):
        """Check if words are being translated"""
        seq = subalign.translate.translate(self.word_sequence, "en", "fr")
        self.assertIn("bonjour", seq[0].word)
        self.assertIn("nom", seq[2].word)

    def test_unknown(self):
        """Check if unknown words are preseverd during translation"""
        seq = subalign.translate.translate(self.word_sequence, "en", "fr")
        self.assertEqual("odskfjoisdjf", seq[3].word)
