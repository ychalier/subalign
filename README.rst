Subtitles Aligner
=================

An automation tool for subtitles synchronisation over video.

Getting Started
---------------

Prerequisites
~~~~~~~~~~~~~

You will need a working Python 3 installation, MKVToolNix_ and FFmpeg_ binaries.
For convenience, you can add ``mkvmerge``, ``mkvextract`` and ``ffmpeg`` to
your ``PATH``. Otherwise you will need to pass the path to those as arguments.

Installation
~~~~~~~~~~~~

Clone the repository, and install the required dependencies with:
::

    pip install -r requirements.txt

This will install NLTK_ (NLP), Pocketsphinx_ (STT) and Word2word_ (Translation).
Those will need additional packages for the different languages you will use
(see the `Supported Languages`_ section).

Word2word_ automatically downloads available language pairs when needed. So
there is nothing to install for now.

For NLTK_, download the ``stopwords`` and ``punkt`` packages by invoking a
Python shell and writing:

.. code-block:: python

    >>> import nltk
    >>> nltk.download("stopwords")
    >>> nltk.download("punkt")

Pocketsphinx_ needs one model for each language. One model consists of:

- One directory containing the acoustic parameters
- One language model file (``*.lm.bin``)
- One phoneme dictionary file (``*.dict``)

To install a new model, create a subfolder ``stt`` at the root directory
of this module. Inside, put one folder per language, named with the `ISO 639-1`_
code of the corresponding language. In these folders, put the three components
for the models, respectively named ``acoustic-model``, ``language-model.lm.bin``
and ``pronounciation-dictionary.dict``. Here is an example file structure:
::

    subalign/
        stt/
            en/
                acoustic-model/
                    feat.params
                    ...
                language-model.lm.bin
                pronounciation-dictionary.dict
            fr/
                acoustic-model/
                    feat.params
                    ...
                language-model.lm.bin
                pronounciation-dictionary.dict
            ...
        subalign/
            __init__.py
            core.py
            ...
        subalign.py
        ...

Pocketsphinx comes by default with an English model, that you can copy and
put in a ``stt/en/`` folder. It is located in ``lib/site-packages/pocketsphinx/model/``.
Do not forget to rename the files!

Usage
~~~~~

Run the ``subalign.py`` script. Use ``-h`` or ``--help`` flags to show
documentation.
::

    usage: subalign.py [-h] [-o OUTPUT_FILE] [-rl REFERENCE_LANGUAGE]
                       [-il INPUT_LANGUAGE] [-v] [--mkvmerge MKVMERGE]
                       [--mkvextract MKVEXTRACT] [--ffmpeg FFMPEG]
                       [-fc FRAGMENT_COUNT] [-fd FRAGMENT_DURATION]
                       [-mi MAX_ITERS] [-tmp TEMP_FOLDER] [-rr] [-rt]
                       [-sm {jaccard-index,overlap-coeff,overlap-count}] [-ks]
                       {align,plot} reference_file input_file


Example
~~~~~~~

Here is an example scenario:
::

    python subalign.py align ~/downloads/utopia-s01e01.mkv ~/downloads/utopia-s01e01-fr.srt -rl en -il fr -o ~/downloads/utopia-s01e01.srt

Supported Languages
-------------------

**tl;dr: Dutch, English, French, German, Greek, Italian, Portugese, Russian and Spanish.**

To check for NLTK_ supported languages, go to the NLTK data folder, and look at
the files under ``tokenizers/punkt/`` and ``corpora/stopwords``. To check for
Pocketsphinx_ supported languages, see
`available models here <https://sourceforge.net/projects/cmusphinx/files/Acoustic%20and%20Language%20Models/>`_.
Word2word_ supports a huge amount of language pairs (3564). See the
`full list here <https://github.com/kakaobrain/word2word/blob/master/word2word/supporting_languages.txt>`_.


+-----------------+----------------+-------------+--------------+
|                 | NLTK Stopwords | NLTK Punkt  | Pocketsphinx |
+=================+================+=============+==============+
| Arabic          |       x        |             |              |
+-----------------+----------------+-------------+--------------+
| Azerbaijani     |       x        |             |              |
+-----------------+----------------+-------------+--------------+
| Catalan         |  x (Spanish)   | x (Spanish) |      x       |
+-----------------+----------------+-------------+--------------+
| Czech           |                |      x      |              |
+-----------------+----------------+-------------+--------------+
| Danish          |       x        |      x      |              |
+-----------------+----------------+-------------+--------------+
| Dutch           |       x        |      x      |      x       |
+-----------------+----------------+-------------+--------------+
| English         |       x        |      x      |      x       |
+-----------------+----------------+-------------+--------------+
| Estonian        |                |      x      |              |
+-----------------+----------------+-------------+--------------+
| Finnish         |       x        |      x      |              |
+-----------------+----------------+-------------+--------------+
| French          |       x        |      x      |      x       |
+-----------------+----------------+-------------+--------------+
| German          |       x        |      x      |      x       |
+-----------------+----------------+-------------+--------------+
| Greek           |       x        |      x      |      x       |
+-----------------+----------------+-------------+--------------+
| Hindi           |                |             |      x       |
+-----------------+----------------+-------------+--------------+
| Hungarian       |       x        |             |              |
+-----------------+----------------+-------------+--------------+
| Indian English  | x (English)    | x (English) |      x       |
+-----------------+----------------+-------------+--------------+
| Indonesian      |       x        |             |              |
+-----------------+----------------+-------------+--------------+
| Italian         |       x        |      x      |      x       |
+-----------------+----------------+-------------+--------------+
| Kazakh          |       x        |             |      x       |
+-----------------+----------------+-------------+--------------+
| Mandarin        |                |             |      x       |
+-----------------+----------------+-------------+--------------+
| Mexican spanish |  x (Spanish)   | x (Spanish) |      x       |
+-----------------+----------------+-------------+--------------+
| Nepali          |       x        |             |              |
+-----------------+----------------+-------------+--------------+
| Norwegian       |       x        |      x      |              |
+-----------------+----------------+-------------+--------------+
| Polish          |                |      x      |              |
+-----------------+----------------+-------------+--------------+
| Portugese       |       x        |      x      |      x       |
+-----------------+----------------+-------------+--------------+
| Romanian        |       x        |             |              |
+-----------------+----------------+-------------+--------------+
| Russian         |       x        |      x      |      x       |
+-----------------+----------------+-------------+--------------+
| Slovene         |       x        |      x      |              |
+-----------------+----------------+-------------+--------------+
| Spanish         |       x        |      x      |      x       |
+-----------------+----------------+-------------+--------------+
| Swedish         |       x        |      x      |              |
+-----------------+----------------+-------------+--------------+
| Tajik           |       x        |             |              |
+-----------------+----------------+-------------+--------------+
| Turkish         |       x        |      x      |              |
+-----------------+----------------+-------------+--------------+

Contributing
------------

Contributions are welcomed. Open issues and pull requests when you want to
submit something.

License
-------

This project is licensed under the MIT License.

.. _MKVToolNix: https://mkvtoolnix.download/downloads.html
.. _FFmpeg: https://www.ffmpeg.org/download.html
.. _NLTK: https://www.nltk.org/
.. _Pocketsphinx: https://pypi.org/project/pocketsphinx/
.. _Word2word: https://pypi.org/project/word2word/
.. _ISO 639-1: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
