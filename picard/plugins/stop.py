# -*- coding: utf-8 -*-

PLUGIN_NAME = "stop"
PLUGIN_AUTHOR = "Wieland Hoffmann"
PLUGIN_DESCRIPTION = """Adds a `stop` function that can be used to stop the
file naming string at a specific point. It's useful if you have several
different file naming schemes with lots of nested `if`s. This does *only* work
for file naming."""
PLUGIN_VERSION = "0.1"
PLUGIN_API_VERSIONS = ["0.15", "0.16"]

from picard.script import register_script_function, ScriptParser

STOP_MARKER = '-\o\-JUSTSTOPHERE-/o/-'


class StoppingScriptParser(ScriptParser):
    def eval(self, script, context=None, file=None):
        result = ScriptParser.eval(self, script, context, file)
        return result.split(STOP_MARKER)[0]

from picard.ui.options import renaming
renaming.ScriptParser = StoppingScriptParser

from picard import file
file.ScriptParser = StoppingScriptParser


def stop(parser, emptyarg):
    return STOP_MARKER

register_script_function(stop)
