PLUGIN_NAME = "Padded {disc,track}numbers"
PLUGIN_AUTHOR = "Wieland Hoffmann"
PLUGIN_DESCRIPTION = \
"""Adds padded disc- and tracknumbers so the length of all disc- and
tracknumbers is the same. They are stored in the `_paddedtracknumber` and
`_paddeddiscnumber` tags."""

PLUGIN_VERSION = "0.1"
PLUGIN_API_VERSIONS = ["0.15"]

from picard.metadata import register_track_metadata_processor

@register_track_metadata_processor
def add_padded_tn(album, metadata, release, track):
    maxlength = len(metadata["totaltracks"])
    islength = len(metadata["tracknumber"])
    metadata["~paddedtracknumber"] = int(maxlength - islength) * "0" +\
                                      metadata["tracknumber"]

@register_track_metadata_processor
def add_padded_dn(album, metadata, release, track):
    maxlength = len(metadata["totaldiscs"])
    islength = len(metadata["discnumber"])
    metadata["~paddeddiscnumber"] = int(maxlength - islength) * "0" +\
                                      metadata["discnumber"]
