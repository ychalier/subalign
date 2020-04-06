"""This module contains the performable actions"""

import logging
import shutil
import os
from .extract import gather_video_properties
from .extract import extract_audio_file
from .extract import convert_audio_for_stt
from .extract import select_track
from .speech import speech_to_text
from .subtitles import SubtitleFactory
from .subtitles import shift_subs
from .translate import translate
from .sequence import WordSequence
from .lang import LANGUAGES


def align(args):
    """Align action"""
    logging.info("Entering align action")
    ref_lang = LANGUAGES[args.reference_language]
    tgt_lang = LANGUAGES[args.input_language]
    if not args.reuse_reference and not args.reuse_target:
        if os.path.isdir(args.temp_folder):
            shutil.rmtree(args.temp_folder, ignore_errors=True)
    os.makedirs(args.temp_folder, exist_ok=True)

    if args.reuse_reference:
        ref_seq = WordSequence.from_file(
            os.path.join(args.temp_folder, "ref_seq.tsv"),
            "utf8")
    else:
        if os.path.splitext(args.reference_file)[1] == ".mkv":
            video_properties = gather_video_properties(
                args.mkvmerge,
                args.reference_file
            )
            track = select_track(video_properties, "audio", ref_lang)
            extract_audio_file(
                args.mkvextract,
                args.reference_file,
                track["id"],
                os.path.join(args.temp_folder, "audio.raw")
            )
            convert_audio_for_stt(
                args.ffmpeg,
                os.path.join(args.temp_folder, "audio.raw"),
                os.path.join(args.temp_folder, "audio.wav"),
            )
        else:
            convert_audio_for_stt(
                args.ffmpeg,
                args.reference_file,
                os.path.join(args.temp_folder, "audio.wav"),
            )
        ref_transcript = speech_to_text(
            os.path.join(args.temp_folder, "audio.wav"),
            args.fragment_count,
            args.fragment_duration,
            ref_lang.iso
        )
        ref_transcript.save(
            os.path.join(args.temp_folder, "transcript.tsv"),
            "utf8"
        )
        ref_seq = WordSequence.from_list(ref_transcript.to_list())
        ref_seq.save(os.path.join(args.temp_folder, "ref_seq.tsv"), "utf8")
    factory = SubtitleFactory("utf8")
    tgt_subs = factory.read(args.input_file)
    if args.reuse_target:
        if os.path.isfile(os.path.join(args.temp_folder, "tgt_seq_translated.tsv")):
            tgt_seq = WordSequence.from_file(
                os.path.join(args.temp_folder, "tgt_seq_translated.tsv"),
                "utf8")
        else:
            tgt_seq = WordSequence.from_file(
                os.path.join(args.temp_folder, "tgt_seq_original.tsv"),
                "utf8")
    else:
        tgt_seq = WordSequence.from_subs(tgt_subs, tgt_lang.nltk, args.keep_subs)
        tgt_seq.save(
            os.path.join(args.temp_folder, "tgt_seq_original.tsv"),
            "utf8"
        )
        if tgt_lang != ref_lang:
            tgt_seq = translate(tgt_seq, tgt_lang.word2word, ref_lang.word2word)
            tgt_seq.save(
                os.path.join(args.temp_folder, "tgt_seq_translated.tsv"),
                "utf8"
            )
    offset = ref_seq.find_offset(
        tgt_seq,
        ref_lang.nltk,
        args.max_iters,
        args.similarity_measure,
    )
    logging.info(
        "Found an offset of %.2f seconds (i.e. target subs are shown too %s)",
        -offset,
        "late" if offset < 0 else "soon"
    )
    factory.write(
        shift_subs(tgt_subs, offset),
        args.output_file,
    )
    return offset


def plot(args):
    """Plot action"""
    logging.info("Entering plot action")
    ref_lang = LANGUAGES[args.reference_language]
    tgt_lang = LANGUAGES[args.input_language]
    factory = SubtitleFactory("utf8")
    WordSequence.from_subs(factory.read(args.reference_file), ref_lang.nltk, args.keep_subs).svg(
        WordSequence.from_subs(factory.read(args.input_file), tgt_lang.nltk, args.keep_subs),
        args.output_file
    )
