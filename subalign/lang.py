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
    "nl": Language("nl", "dut", "nl", "dutch"),
    "en": Language("en", "eng", "en", "english"),
    "fr": Language("fr", "fre", "fr", "french"),
    "de": Language("de", "ger", "de", "german"),
    "el": Language("el", "gre", "el", "greek"),
    "it": Language("it", "ita", "it", "italian"),
    "pt": Language("pt", "por", "pt", "portuguese"),
    "ru": Language("ru", "rus", "ru", "russian"),
    "es": Language("es", "spa", "es", "spanish"),
}
