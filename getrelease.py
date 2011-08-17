#! /usr/bin/env python2
"""
Retrieve a release by ID and display it in mediawiki markup

Usage:
    python getrelease.py release-id
"""

import sys
import musicbrainz2.webservice as ws

if len(sys.argv) < 2:
    sys.exit(__doc__)

q = ws.Query()

try:
    inc = ws.ReleaseIncludes(tracks=True)
    release = q.getReleaseById(sys.argv[1], inc)
except ws.WebServiceError, e:
    sys.exit(e)

print "{|"
print "| '''ADD YOUR TABLE HEADER HERE'''"
for track in release.tracks:
    print "|-"
    print "| %s" % track.title
print "}"
