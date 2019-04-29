"""Subtitle aligner

arguments:  <reference-file> <target-file> <output-filename>
            [lang-target=fr] [lang-reference=en]

The target file will be shifted to correspond to the reference file. The output
will be written to an external file under the SRT format.
"""

from googletrans import Translator
import copy
import sys

from subtitles import Subtitles

def translate(subs, n, src, dest):
    print("Translating from", src, "to", dest)
    new_subs = Subtitles()
    translator = Translator()
    for sub in subs.data[:n]:
        new_sub = copy.deepcopy(sub)
        new_sub.text = translator.translate(sub.text, src=src, dest=dest).text
        new_subs.add(new_sub)
    return new_subs

def offset(tgt, ref):
    # sub to sub bag-of-words similarity
    sim = []
    for sub in tgt:
        sim.append([sub.sim(d) for d in ref])
    # aggregated in diagonals (consecutive subs)
    trailing = []
    for origin in range(len(ref) - len(tgt)):
        buffer = []
        for current in range(len(tgt)):
            buffer.append(sim[current][origin+current])
        trailing.append(buffer)
    # average to extract highest conitunuous sub matching
    avg = [sum(row)/len(row) for row in trailing]
    sub_offset = avg.index(max(avg))
    # grab the highest match from the highest matching diagonal
    sub_origin = trailing[sub_offset].index(max(trailing[sub_offset]))
    return ref[sub_origin+sub_offset].start - tgt[sub_origin].start

def shift(subs, offset):
    new_subs = copy.deepcopy(subs)
    for sub in new_subs:
        sub.start = sub.start + offset
        sub.stop = sub.stop + offset
    return new_subs

def align(tgt, ref, filename, lang_tgt, lang_ref):
    tsl = translate(tgt, 20, lang_tgt, lang_ref)
    shift(tgt, offset(tsl, ref)).save(filename)

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
