# Subtitles Aligner

## Setup

### Google Translate

For now, the program uses [Googletrans](https://pypi.org/project/googletrans/),
that you will have to install to use the program.

```
pip install googletrans
```

### MKV Support

If you want to use MKV files, install `mkvtoolnix`:

```
sudo apt-get install mkvtoolnix
```

See the [official website](https://mkvtoolnix.download/downloads.html) for more
information about that.

## Usage

### Problem Statement

The program works by aligning two different subtitles files. One is the
**reference**, that is already synced to the video. For instance, it might be
an already existing subtitle track within the .mkv you downloaded. Then, for
linguistics reasons, you want to use subtitles downloaded separately from the
video, and that might not be synced. This file will be called the **target**
file.

### What the Program Does

What the program does, is translating the *target* file into the language of the
*reference* file, and then align the translation with the reference. Then an
offset is computed and applied to all entries in the *target* file.

Default syntax is:

```
python3 aligner.py <reference-file> <target-file> <output-filename>
```

The output file will be under the SRT format.

### What the Program Does Not (*for now*)

It does not handle framerate issues. It does not understand nor export other
subtitle format than SRT. Those issues can be tackled by other existing programs
such as [Gnome Subtitles](https://github.com/GNOME/gnome-subtitles).
