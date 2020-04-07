"""Setup script"""

import os
from setuptools import setup
import subalign

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='subalign',
    version=subalign.__version__,
    packages=["subalign"],
    include_package_data=True,
    license=subalign.__license__,
    description=subalign.__doc__,
    long_description=README,
    url='https://github.com/ychalier/subalign',
    author=subalign.__author__,
    author_email=subalign.__email__,
    keywords="subtitles-aligner speech-to-text translation",
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Multimedia :: Video",
        "Topic :: Text Processing",
    ],
    install_requires=[
        "nltk",
        "pocketsphinx",
        "word2word"
    ],
)
