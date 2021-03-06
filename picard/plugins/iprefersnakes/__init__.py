# coding: utf-8
# Copyright © 2015, 2017 Wieland Hoffmann
# License: MIT, see LICENSE for details
PLUGIN_NAME = "File naming via Python"
PLUGIN_AUTHOR = "Wieland Hoffmann"
PLUGIN_DESCRIPTION = """This plugins allows writing the file naming string in
Python instead of tagger script. Replace the tagger script with
$iprefersnakes() and write the Python code in the provided options page."""
PLUGIN_VERSION = "0.1"
PLUGIN_API_VERSIONS = ["2.0"]


from .options_iprefersnakes import Ui_IPreferSnakesOptionsPage
from picard import config
from picard.ui.options import OptionsPage, OptionsCheckError, register_options_page
from picard.script import register_script_function


_FUNCTION_NAME = "ips_func"
_FUNCTION_TEMPLATE = \
"""
from picard.config import setting
def {name}():
    {code}
"""


def compile_code(code, parser=None):
    obj = compile(_FUNCTION_TEMPLATE.format(
            name=_FUNCTION_NAME,
            code=code.replace(
                "\n",
                "\n    ")),
        "<iprefersnakes_inline>",
        "exec")
    environment = {}
    if parser is not None:
        environment["metadata"] = parser.context
    exec(obj, environment)
    return environment[_FUNCTION_NAME]


@register_script_function
def iprefersnakes(parser):
    return compile_code(config.setting["iprefersnakes_code"],
                        parser)()


class IPreferSnakesOptionsPage(OptionsPage):
    NAME = "iprefersnakes"
    TITLE = "I Prefer Snakes"
    PARENT = "filerenaming"

    options = [
        config.TextOption("setting", "iprefersnakes_code", "")
    ]

    def __init__(self, parent=None):
        super(IPreferSnakesOptionsPage, self).__init__()
        self.ui = Ui_IPreferSnakesOptionsPage()
        self.ui.setupUi(self)
        self.ui.code.textChanged.connect(self.check_code)

    def load(self):
        self.ui.code.setPlainText(self.config.setting["iprefersnakes_code"])

    def save(self):
        self.config.setting["iprefersnakes_code"] = self.ui.code.toPlainText()

    def check(self):
        code = self.ui.code.toPlainText()
        try:
            compile_code(code)
        except SyntaxError as e:
            raise OptionsCheckError("Compilation failure", e)

    def check_code(self):
        self.ui.code_error.setStyleSheet("")
        self.ui.code_error.setText("")
        code = self.ui.code.toPlainText()
        try:
            compile_code(code)
        except SyntaxError as e:
            # We add some lines at the top, substract them again
            e.lineno = e.lineno - 3
            self.ui.code_error.setStyleSheet(self.STYLESHEET_ERROR)
            self.ui.code_error.setText(e)


register_options_page(IPreferSnakesOptionsPage)
