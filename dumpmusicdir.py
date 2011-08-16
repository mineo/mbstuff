#!/usr/bin/env python2
"""
Dumps the metadata of music files in a directory in a format usable by
MusicBrainz' release editor

Usage:
    dumpmusicdir.py /path/to/the/folder
"""

import mutagen
import mutagen.easyid3
import sys
import os

from datetime import timedelta

to_time = lambda seconds: timedelta(seconds=seconds)

def main():
    if len(sys.argv) < 2:
        exit(__doc__)

    for _object in os.listdir(sys.argv[1]):
        fpath = os.path.join(sys.argv[1], _object)

        if not os.path.isfile(fpath):
            continue

        if _object[-3:] == "mp3":
            _file = mutagen.easyid3.EasyID3(fpath)
        else:
            _file = mutagen.File(fpath)

        if _file is None:
            continue
        print _file["tracknumber"][0],
        print _file["title"][0], "-",
        print _file["artist"][0],
        if isinstance(_file, mutagen.easyid3.EasyID3):
            print
            continue

        print to_time(_file.info.length)

if __name__ == '__main__':
    main()
