"""Wrapper for mkvmerge, mkvextract and ffmpeg tools"""
import os
import json
import subprocess
import logging


def gather_video_properties(mkvmerge, video_path):
    """Use the mkvmerge --identify option to extract tracks information from a
       video file.
    """
    logging.debug(
        "Extracting video properties of %s",
        os.path.realpath(video_path)
    )
    command = [mkvmerge, "-J", os.path.realpath(video_path)]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    return json.load(process.stdout)


def select_track(video_properties, track_type, language):
    """Select a track from a video file with matching language"""
    tracks = list()
    selection = None
    for track in video_properties["tracks"]:
        if track["type"] != track_type:
            continue
        tracks.append(track)
        if track["properties"]["language"] == language.mkvmerge:
            selection = track
    if len(tracks) == 0:
        logging.warning("No %s track found", track_type)
        return None
    logging.debug("Found %d %s track(s)", len(tracks), track_type)
    if selection is None:
        logging.warning(
            "No %s track with language '%s' found; selecting the first one",
            track_type,
            language.mkvmerge
        )
        selection = tracks[0]
    logging.debug(
        "Selected %s track #%d (language: %s)",
        track_type,
        selection["id"],
        selection["properties"]["language"]
    )
    return selection


def extract_audio_file(mkvextract, video_path, track_id, output_file):
    """Extract an audio track from a video file using mkvextract"""
    logging.info(
        "Extracting audio track %d of %s to %s",
        track_id,
        os.path.realpath(video_path),
        os.path.realpath(output_file)
    )
    command = [
        mkvextract,
        os.path.realpath(video_path),
        "tracks", "%s:%s" % (track_id, output_file)
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    process.wait()
    output = process.stdout.read().decode("utf8").strip()
    if len(output) > 0:
        logging.error(output)


def convert_audio_for_stt(ffmpeg, source, destination):
    """Convert an audio file, using FFMPEG, to the CMUSphinx input format:
       16kHz sampling frequency, mono, 16bit PCM little endian.
    """
    logging.info(
        "Converting audio from %s to %s",
        os.path.realpath(source),
        os.path.realpath(destination)
    )
    command = [
        ffmpeg,
        "-v", "quiet",
        "-i", os.path.realpath(source),
        "-ar", "16000",
        "-ac", "1",
        # "-f", "s16le",
        "-f", "wav",
        # "-flags",
        "-bitexact",
        "-acodec", "pcm_s16le",
        "-y",
        os.path.realpath(destination),
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    process.wait()
