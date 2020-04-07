# pylint: disable=C0103
"""
"""
import argparse
import logging
import subalign.core


parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument("action", type=str, help="action to perform",
                    choices=["align", "plot"])
parser.add_argument("reference_file", type=str,
                    help="path to the reference video file")
parser.add_argument("input_file", type=str,
                    help="path to the input subtitle file")
parser.add_argument("-o", "--output-file", type=str,
                    help="path to the output subtitle file",
                    default="subtitles-aligned.srt", dest="output_file")
parser.add_argument("-rl", "--reference-language", type=str,
                    help="reference file language (ISO 639-1)",
                    default="en", dest="reference_language")
parser.add_argument("-il", "--input-language", type=str,
                    help="input file language (ISO 639-1)",
                    default="fr", dest="input_language")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="display debug information")
parser.add_argument("--mkvmerge", type=str,
                    help="path to MKVMerge executable",
                    default="mkvmerge")
parser.add_argument("--mkvextract", type=str,
                    help="path to MKVExtract executable",
                    default="mkvextract")
parser.add_argument("--ffmpeg", type=str,
                    help="path to FFMPEG executable",
                    default="ffmpeg")
parser.add_argument("-fc", "--fragment-count", type=int,
                    help="number of speech-to-text extracted fragment",
                    default=10, dest="fragment_count")
parser.add_argument("-fd", "--fragment-duration", type=int,
                    help="duration of one speech-to-text fragment in seconds",
                    default=5, dest="fragment_duration")
parser.add_argument("-mi", "--max-iters", type=int,
                    help="maximum iterations for one round of alignment",
                    default=100, dest="max_iters")
parser.add_argument("-tmp", "--temp_folder", type=str,
                    help="path to the temporary folder",
                    default="tmp")
parser.add_argument("-rr", "--reuse-reference", action="store_true",
                    help="re-use previously computed reference WordSequence")
parser.add_argument("-rt", "--reuse-target", action="store_true",
                    help="re-use previously computed target WordSequence")
parser.add_argument("-sm", "--similarity-measure", type=str,
                    help="similarity function to use to compare buckets",
                    choices=["jaccard-index",
                             "overlap-coeff", "overlap-count"],
                    default="overlap-coeff", dest="similarity_measure")
parser.add_argument("-ks", "--keep-subs", action="store_true",
                    help="prevent subtitles split into arbitrary lengthed words",
                    dest="keep_subs")
args = parser.parse_args()
log_format = "%(asctime)s\t%(levelname)s\t%(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)
if args.action == "align":
    subalign.core.align(args)
elif args.action == "plot":
    subalign.core.plot(args)
