PLUGIN_NAME = 'Add to collection'
PLUGIN_AUTHOR = 'Wieland Hoffmann'
PLUGIN_DESCRIPTION = 'Adds an $add_to_collection function'
PLUGIN_VERSION = '0.1'
PLUGIN_API_VERSIONS = ['2.0']
from picard import collection
from picard.script import register_script_function


def callback(*args, **kwargs):
    pass


def add_to_collection(parser, collectionid):
    mbid = parser.context['musicbrainz_albumid']
    try:
        thiscollection = collection.user_collections[collectionid]
    except KeyError:
        return ''
    if str(mbid) in thiscollection.releases or mbid in thiscollection.pending:
        return ''
    thiscollection.add_releases(set([mbid]), callback)
    return ''


register_script_function(add_to_collection)
