PLUGIN_NAME = "Keep tags"
PLUGIN_AUTHOR = "Wieland Hoffmann"
PLUGIN_DESCRIPTION = "Adds a $keep() function to delete all tags except the ones that you want"

PLUGIN_VERSION = "0.1"
PLUGIN_API_VERSIONS = ["0.15"]

from picard.script import register_script_function


def transltag(tag):
    if tag.startswith("~"):
        return "_" + tag[1:]
    return tag


def keep(parser, *keeptags):
    for tag in parser.context.keys():
        if transltag(tag) not in keeptags and not tag.startswith("musicbrainz_"):
            parser.context.pop(tag, None)
    return ""

register_script_function(keep)
