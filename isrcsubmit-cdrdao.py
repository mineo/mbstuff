#!/usr/bin/env python2
# Copyright 2010 Johannes Dewender ( brainz at JonnyJD.net ) 
# Copyright 2011 Wieland Hoffmann
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Submits ISRCs to MusicBrainz

heavily inspired by http://kraehen.org/isrcsubmit.py
"""
import getpass
import subprocess

from musicbrainz2.disc import readDisc, DiscError, getSubmissionUrl
from musicbrainz2.webservice import WebService, Query, ReleaseFilter
from musicbrainz2.webservice import WebServiceError, ReleaseIncludes
from datetime import datetime
from os import remove
from sys import version_info

_offset_help = \
"""Offset to add to every track number
This is useful for releases with multi-disc releases.
Currently you'll only get one big release from the webservice.
Example:
    CD1: 25 tracks
    CD2: 26 tracks
If you want to submit ISRCs for CD2, you'll have to specify an offset of 25"""

def main():
    print """ATTENTION: Please read the help (-h) if you want to submit ISRCs for a
    release with multiple discs"""
    if version_info >= (2,7):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("-u", "--user", type=str, help="Username")
        parser.add_argument("-p", "--password", type=str, help="Password")
        parser.add_argument("-d", "--device", type=str, default="/dev/sr0",
                help="Device name (default is /dev/sr0)")
        parser.add_argument("-o", "--offset", type=int, default=0,
                help=_offset_help)

        args = parser.parse_args()
    else:
        import optparse
        parser = optparse.OptionParser()
        parser.add_option("-u", "--user", type=str, help="Username")
        parser.add_option("-p", "--password", type=str, help="Password")
        parser.add_option("-d", "--device", type=str, default="/dev/sr0",
                help="Device name (default is /dev/sr0)")
        parser.add_option("-o", "--offset", type=int, default=0,
                help=_offset_help)
        (args, options) = parser.parse_args()
    if not args.user:
        exit("No username given")

    if not args.password:
        password = getpass.getpass()
    else:
        password = args.password

    try:
        disc = readDisc(args.device)
    except DiscError, e:
        exit("DiscID calculation failed: %s" % e)

    ws = WebService(username=args.user, password=password)
    q = Query(ws)

    filter = ReleaseFilter(discId=disc.id)

    try:
        results = q.getReleases(filter=filter)
    except WebServiceError, e:
        exit("An error occured while communicating with MusicBrainz: %s" % e)

    if len(results) == 0:
        print "The disc is not in the database"
        print "Please submit it with: %s" % getSubmissionUrl(disc)
        exit(1)
    elif len(results) > 1:
        print "This Disc ID is ambiguous:"
        for i in range(len(results)):
            release = results[i].release
            print str(i)+":", release.getArtist().getName(),
            print "-", release.getTitle(),
            print "(" + release.getTypes()[1].rpartition('#')[2] + ")"
            print release.getId()
        num = -1
        while True:
            try:
                num =  raw_input("Which one do you want? [0-%d] " % i)
                result = results[int(num)]
            except (IndexError, ValueError):
                continue
            break
    else:
        result = results[0]

    include = ReleaseIncludes(artist=True, tracks=True, isrcs=True)
    try:
        release = q.getReleaseById(result.getRelease().getId(), include=include)
    except WebServiceError, e:
        print "Couldn't fetch release:", str(e)
        exit(1)
    print 'Artist:\t\t', release.getArtist().getName()
    print 'Release:\t', release.getTitle()
    tracks = release.getTracks()

    filename = "/tmp/cdrdao-%s.toc" % datetime.now()
    try:
        proc = subprocess.Popen(["cdrdao", "read-toc", "--fast-toc", "--device",
                args.device, "-v", "0", filename], stderr=subprocess.PIPE,
                stdout=subprocess.PIPE)
        proc.wait()
    except Exception, e:
        exit("Exception while calling cdrdao: %s" % str(e))
    if proc.returncode != 0:
        exit("cdrdao returned with return code %i" % proc.returncode)

    tracks2isrcs = dict()
    tracknum = 0

    with open(filename, "r") as tocfile:
        for line in tocfile:
            sline = line.split(" ")
            if sline[0] == "//":
                tracknum = int(sline[2]) - 1 + args.offset
            elif sline[0] == "ISRC":
                isrc = sline[1][1:-2]
                if isrc not in (tracks[tracknum].getISRCs()):
                    tracks2isrcs[tracks[tracknum].getId()] = isrc

    if len(tracks2isrcs) == 0:
        print "No new ISRCs could be found."
    else:
        vals = tracks2isrcs.values()
        for key, val in tracks2isrcs.items():
            if vals.count(val) > 1:
                print "The ISRC %s appears multiple times, I'm not going to submit it"\
                % val
                tracks2isrcs.pop(key)
                continue
            print "The ISRC %s will be attached to %s" % (val, key)
            if raw_input("Is this correct? [y/N]").lower() != "y":
                tracks2isrcs.pop(key)

        if len(tracks2isrcs.keys()) > 0:
            try:
                q.submitISRCs(tracks2isrcs)
                print "Successfully submitted", len(tracks2isrcs), "ISRCs."
            except WebServiceError, e:
                print "Couldn't send ISRCs:", str(e)
        else:
            print "Nothing was submitted to the server."
    remove(filename)


if __name__ == '__main__':
    main()
