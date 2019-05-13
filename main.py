"""Subtitle aligner

arguments:  <reference-file> <target-file> <output-filename>
            [lang-target=fr] [lang-reference=en]

The target file will be shifted to correspond to the reference file. The output
will be written to an external file under the SRT format.
"""

import sys

from subtitles import Subtitles
from translator import translate
from aligner import process

def align(tgt, ref, filename, lang_tgt, lang_ref):
    tsl = tgt  # translate(tgt, lang_tgt, lang_ref)
    process(ref, tsl)
    tsl.save(filename)

if __name__ == "__main__":
    if len(sys.argv) not in [4, 5, 6]:
        print(__doc__)
        exit()
    ref_file, tgt_file, out_file = sys.argv[1:4]
    lang_tgt, lang_ref = "fr", "en"
    for i in range(4, len(sys.argv)):
        if "lang-target" in sys.argv[i]:
            lang_tgt = sys.argv[i].split("=")[1]
        elif "lang-reference" in sys.argv[i]:
            lang_ref = sys.argv[i].split("=")[1]
    ref = Subtitles.from_file(ref_file)
    tgt = Subtitles.from_file(tgt_file)
    align(tgt, ref, out_file, lang_tgt, lang_ref)
