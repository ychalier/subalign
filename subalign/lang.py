"""Hardcoded language nomenclatures"""

class Language:
    """Wrapper for different language nomenclatures depending on the module."""

    def __init__(self, iso, mkvmerge_, word2word_, nltk_):
        self.iso = iso
        self.mkvmerge = mkvmerge_
        self.word2word = word2word_
        self.nltk = nltk_

    def __eq__(self, other):
        return self.iso == other.iso

    def __hash__(self):
        return hash(self.iso)


LANGUAGES = {
    "fr": Language("fr", "fre", "fr", "french"),
    "en": Language("en", "eng", "en", "english")
}
