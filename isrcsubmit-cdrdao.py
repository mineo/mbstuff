#!/usr/bin/env python2
# Copyright 2010 Johannes Dewender ( brainz at JonnyJD.net )
# Copyright 2011 Wieland Hoffmann
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
import discid
import getpass
import musicbrainzngs
import optparse
import subprocess

from datetime import datetime
from os import remove
from sys import exit, version_info
def main():
    parser = optparse.OptionParser()
    parser.add_option("-u", "--user", type=str, help="Username")
    parser.add_option("-p", "--password", type=str, help="Password")
    parser.add_option("-d", "--device", type=str, default=discid.DEFAULT_DEVICE,
            help="Device name, the default is %s" % discid.DEFAULT_DEVICE)
    (args, options) = parser.parse_args()

    if not args.user:
        exit("No username given")

    if not args.password:
        password = getpass.getpass()
    else:
        password = args.password

    _id = None
    submission_url = None
    with discid.DiscId() as disc:
        disc.read(args.device)
        _id = disc.id
        submission_url = disc.submission_url

    if _id is None:
        exit("No discid could be calculated")

    musicbrainzngs.auth(args.user, password)
    musicbrainzngs.set_useragent("isrcsubmit-cdrdao", "0.2", "Mineo@Freenode")

    results = musicbrainzngs.get_releases_by_discid(
            _id, includes=["recordings", "isrcs",
            "artist-credits"])["disc"]["release-list"]

    if len(results) == 0:
        print "The disc is not in the database"
        print "Please submit it with: %s" % submission_url
        exit(1)
    elif len(results) > 1:
        print "This Disc ID is ambiguous:"
        for i, release in enumerate(results):
            print str(i)+":", release["artist-credit-phrase"]
            print "-", release["title"]
            print release["id"]
        num = -1
        while True:
            try:
                num =  raw_input("Which one do you want? [0-%d] " % i)
                release = results[int(num)]
            except (IndexError, ValueError):
                continue
            break
    else:
        release = results[0]

    print 'Artist: %s' % release["artist-credit-phrase"]
    print 'Release: %s' % release["title"]

    real_medium = None
    for medium in release["medium-list"]:
        for mdisc in medium["disc-list"]:
            print mdisc
            if mdisc["id"] == _id:
                real_medium = medium
                break

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

    tracks = real_medium["track-list"]
    tracks2isrcs = dict()
    tracknum = 0

    with open(filename, "r") as tocfile:
        for line in tocfile:
            sline = line.split(" ")
            if sline[0] == "//":
                tracknum = int(sline[2]) - 1
            elif sline[0] == "ISRC":
                isrc = sline[1][1:-2]
                try:
                    if isrc not in tracks[tracknum]["recording"]["isrc-list"]:
                        tracks2isrcs[tracks[tracknum]["recording"]["id"]] = [isrc]
                except KeyError:
                    tracks2isrcs[tracks[tracknum]["recording"]["id"]] = [isrc]

    if len(tracks2isrcs) == 0:
        print "No new ISRCs could be found."
    else:
        vals = tracks2isrcs.values()
        print "\nISRC         | Recording"
        print "-" * 13 + "+" + "-" * 66
        for key, val in sorted(tracks2isrcs.items(), key=lambda keyval: keyval[1]):
            if vals.count(val) > 1:
                print "The ISRC %s appears multiple times, I'm not going to submit it"\
                % val
                tracks2isrcs.pop(key)
                continue

            print "%s | %s" % (val, key)

        if raw_input("Is this correct? [y/N]").lower() == "y":
            if len(tracks2isrcs.keys()) > 0:
                try:
                    musicbrainzngs.submit_isrcs(tracks2isrcs)
                    print "Successfully submitted", len(tracks2isrcs), "ISRCs."
                except musicbrainzngs.WebServiceError, e:
                    print "Couldn't send ISRCs:", str(e)
            else:
                print "Nothing was submitted to the server."
    remove(filename)


if __name__ == '__main__':
    main()
