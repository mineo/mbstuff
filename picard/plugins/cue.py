# -*- coding: utf-8 -*-

PLUGIN_NAME = "cuesheets"
PLUGIN_AUTHOR = "Wieland Hoffmann"
PLUGIN_DESCRIPTION = "Support for cuesheets"
PLUGIN_VERSION = "0.1"
PLUGIN_API_VERSIONS = ["0.15", "0.16"]

import os
import os.path
import shutil

from picard.formats import register_format

from functools import partial
from PyQt4 import QtCore
from picard.file import File
from picard.metadata import Metadata
from picard.util import encode_filename


class CueSheetBase(File):
    _translate = {
        "PERFORMER": "albumartist",
        "TITLE": "album",
        "CATALOG": "barcode",
    }

    _rem_translate = {
        "ALBUMARTIST": "albumartist",
        "DATE": "date",
        "ORIGINALDATE": "originaldate",
        "COMPOSER": "composer",
        "LYRICIST": "lyricist",
        "CONDUCTOR": "conductor",
        "REMIXER": "remixer",
        "ARRANGER": "arranger",
        "ENGINEER": "engineer",
        "PRODUCER": "producer",
        "DJMIXER": "djmixer",
        # TODO performer?
        # TODO comment"
        # TODO lyrics
        "TOTALTRACKS": "totaltracks",
        "DISCNUMBER": "discnumber",
        "TOTALDISCS": "totaldiscs",
        "COMPILATION": "compilation",
        "GENRE": "genre",
        "BPM": "bpm",
        "MOOD": "mood",
        "ISRC": "isrc",
        "COPYRIGHT": "copyright",
        "MEDIA": "media",
        "LABEL": "label",
        "CATALOGNUMBER": "catalognumber",
        "BARCODE": "barcode",
        "ALBUMSORT": "albumsort",
        "ALBUMARTISTSORT": "albumartistsort",
        "ARTISTSORT": "artistsort",
        "COMMENT": "comment",
        "MUSICBRAINZ_TRACKID": "musicbrainz_trackid",
        "MUSICBRAINZ_ARTIST": "musicbrainz_artistid",
        "MUSICBRAINZ_ALBUM_ID": "musicbrainz_albumid",
        "MUSICBRAINZ_ALBUM_ARTIST_ID": "musicbrainz_albumartistid",
        "MUSICBRAINZ_TRMID": "musicbrainz_trmid",
        "DISCID": "musicbrainz_discid",
        "MUSICIP_PUID": "musicip_puid",
        "FINGERPRINT": "musicip_fingerprint",
        "RELEASESTATUS": "releasestatus",
        "RELEASETYPE": "releasetype",
        "RELEASECOUNTRY": "releasecountry",
        "SCRIPT": "script",
        "LANGUAGE": "language",
        "MUSICBRAINZ_RELEASEGROUPID": "musicbrainz_releasegroupid",
        "MUSICBRAINZ_WORKID": "musicbrainz_workid",
        "LICENSE": "license",
    }

    _rtranslate = dict([(v, k) for k, v in _translate.iteritems()])
    _rtranslate.update(dict([(v, "REM %s" % k) for k, v in _rem_translate.iteritems()]))

    def kv_to_metadata(self, k, v, metadata):
        try:
            if k == "REM":
                splitv = v .split()
                k = splitv[0]
                v = " ".join(splitv[1:])
                k = self._rem_translate[k]
            else:
                k = self._translate[k]
            metadata.add(k, v.strip('"'))
        except KeyError:
            pass

    def metadata_to_kv(self):
        for key, value in self.metadata.iteritems():
            if key in self._rtranslate:
                if key == "album":
                    continue
                yield '%s "%s"'.encode("utf-8") % (self._rtranslate[key], value)


class CueSheetTrack(CueSheetBase):
    _translate = CueSheetBase._translate

    _tracktranslate = {
        "TITLE": "title",
        "PERFORMER": "artist",
        "ISRC": "isrc"
    }

    _translate.update(_tracktranslate)
    _rtranslate = CueSheetBase._rtranslate
    _rtranslate.update(dict([(v, k) for k, v in _translate.iteritems()]))

    def __init__(self, filename, parent, tracknumber, start_metadata=None):
        self.cueparent = parent
        self.parent = parent.parent
        self.indexes = {}
        CueSheetBase.__init__(self, "%s #%s" % (filename, tracknumber))
        tracknumber = int(tracknumber.split()[0])
        self._tracknumber = tracknumber
        self.move(parent.parent)
        if start_metadata is not None:
            self.metadata.copy(start_metadata)
        self.metadata.add("tracknumber", str(tracknumber))


    def _load(self, lines):
        metadata = Metadata()
        metadata.copy(self.metadata)

        metadata.add("album", self.metadata.get("title"))
        del metadata["title"]
        for line in lines:
            splitline = line.split()
            # linetokv?
            key = splitline[0]
            value = " ".join(splitline[1:])
            if key == "INDEX":
                index, value = value.split()
                self.indexes[index] = value
            elif not key == "TRACK":
                self.kv_to_metadata(key, value, metadata)
        return metadata

    def can_analyze(self):
        return False

    def _save_and_rename(self, *args):
        return self.cueparent._save_and_rename(*args)

    def supports_tag(self, name):
        return name in self._rtranslate or name == "tracknumber"


class CueSheet(CueSheetBase):
    EXTENSIONS = [".cue"]
    NAME = "Cuesheet"

    def __init__(self, filename):
        CueSheetBase.__init__(self, filename)
        self.filename = filename
        self.tracks = []
        self.fileline = None

    def _load(self, filename):
        self.log.debug("Loading file %r", filename)
        metadata = Metadata()
        do_tracks = False
        temp_lines = {}
        current_track = None

        with open(filename, "rb") as cuesheet:
            for line in cuesheet:
                line = line.decode("utf-8")
                splitline = line.split()
                key = splitline[0]
                value = " ".join(splitline[1:]).strip()
                if not do_tracks:
                    if not key == "TRACK":
                        if key == "FILE":
                            self.fileline = value
                        else:
                            self.kv_to_metadata(key, value, metadata)
                    else:
                        do_tracks = True
                        current_track = value.split()[0]
                        temp_lines[current_track] = []
                else:
                    if key == "TRACK":
                        current_track = value.split()[0]
                        temp_lines[current_track] = []
                    temp_lines[current_track].append(line)

        for k, v in temp_lines.items():
            fake_filename = u"%s #%s" % (filename, k)
            cuefile = CueSheetTrack(filename, self, k, metadata)
            self.tracks.append(cuefile)
            self.tagger.files[fake_filename] = cuefile
            self.tagger.load_queue.put((
                partial(cuefile._load, v),
                partial(cuefile._loading_finished,
                    self.tagger._file_loaded),
                QtCore.Qt.LowEventPriority + 1))
        self.tagger.remove_files([self])
        return metadata

    def _rename(self, old_filename, metadata, settings):
        old_dir = os.path.dirname(self.filename)
        new_dir = os.path.dirname(encode_filename(
                                    self._make_filename(old_filename,
                                                        metadata,
                                                        settings)))
        filename = os.path.basename(old_filename)
        new_filename = os.path.join(new_dir, filename)
        audiofile = " ".join(self.fileline.split()[0:-1]).strip('"')

        old_audiofile = os.path.join(old_dir, audiofile)
        new_audiofile = os.path.join(new_dir, audiofile)

        if not os.path.isdir(new_dir):
            os.makedirs(new_dir)

        if os.path.exists(old_filename):
            self.log.debug("Moving file %r => %r", old_filename, new_filename)
            shutil.move(encode_filename(old_filename), encode_filename(new_filename))
        if os.path.exists(old_audiofile):
            self.log.debug("Moving file %r => %r", old_audiofile, new_audiofile)
            shutil.move(encode_filename(old_audiofile), encode_filename(new_audiofile))
        return new_filename

    def _save(self, filename, metadata, settings):
        with open(self.filename + "", "w") as cuesheet:
            _write = partial(writeline, cuesheet)
            _write('PERFORMER "%s"' %
                    (self.tracks[0].metadata.get("albumartist")))
            _write('TITLE "%s"' %
                    (self.tracks[0].metadata.get("album")))
            _write('FILE %s' % self.fileline)
            self.tracks.sort(key=lambda track: track.tracknumber)
            for track in self.tracks:
                _write("TRACK %02i AUDIO" % track.tracknumber, 2)
                for index, value in track.indexes.iteritems():
                    _write("INDEX %s %s" % (index, value), 4)
                for line in track.metadata_to_kv():
                    _write(line, 4)

    def _save_and_rename(self, old_filename, metadata, settings):
        self._save(old_filename, metadata, settings)
        return self._rename(self.filename, metadata, settings)

def writeline(_file, line, indent=0):
        _line = b" " * indent + line + b"\n"
        _line = _line.encode("utf-8")
        _file.write(_line)

register_format(CueSheet)
