# coding: utf-8
# Copyright © 2015 Wieland Hoffmann
# License: MIT, see LICENSE for details
PLUGIN_NAME = "bla"
PLUGIN_AUTHOR = "Wieland Hoffmann"
PLUGIN_DESCRIPTION = ""
PLUGIN_VERSION = "0.1"
PLUGIN_API_VERSIONS = ["1.3"]


from .options_iprefersnakes import Ui_IPreferSnakesOptionsPage
from picard import config
from picard.ui.options import OptionsPage, OptionsCheckError, register_options_page
from picard.script import register_script_function


_FUNCTION_NAME = "ips_func"
_FUNCTION_TEMPLATE = \
"""
from picard.config import setting
def {name}(metadata):
    {code}
"""


def compile_code(code):
    obj = compile(_FUNCTION_TEMPLATE.format(
            name=_FUNCTION_NAME,
            code=code.replace(
                "\n",
                "\n    ")),
        "<iprefersnakes_inline>",
        "exec")
    environment = {}
    exec(obj, environment)
    return environment[_FUNCTION_NAME]


@register_script_function
def iprefersnakes(parser):
    return compile_code(unicode(config.setting["iprefersnakes_code"]))(parser.context)


class IPreferSnakesOptionsPage(OptionsPage):
    NAME = "iprefersnakes"
    TITLE = "I Prefer Snakes"
    PARENT = "plugins"

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
        self.config.setting["iprefersnakes_code"] = unicode(self.ui.code.toPlainText())

    def check(self):
        code = unicode(self.ui.code.toPlainText())
        try:
            compile_code(code)
        except SyntaxError as e:
            raise OptionsCheckError("Compilation failure", unicode(e))

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
            self.ui.code_error.setText(unicode(e))


register_options_page(IPreferSnakesOptionsPage)
