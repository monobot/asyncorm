import logging

logger = logging.getLogger("asyncorm_stream")

TEMPLATE_TEXT = """\
from asyncorm.models.app_migrator import MigrationBase
from asyncorm.orm_migrations.migration_actions import *


"""


class MigrationConstructor(object):
    def __init__(self, file_name, depends, actions, initial=False):
        self.file_name = file_name
        with open(self.file_name, "w") as f:
            f.write(TEMPLATE_TEXT)

        self._write(0, "class Migration(MigrationBase):\n")

        self._initial_creator(initial)
        self._depends_creator(depends)
        self._actions_creator(actions)

    @staticmethod
    def tabulation(tab_level):
        if tab_level:
            return "    " * tab_level
        return ""

    def _write(self, tab_level, txt):
        with open(self.file_name, "a") as myfile:
            myfile.write(self.tabulation(tab_level) + txt)

    def _write_dictformater(self, tab_level, name, content, notrail=False, asignation=False):
        end_singleline = notrail and "'{}': {{}}\n" or "'{}': {{}},\n"
        end_multistr = notrail and "'{}': '{}'\n" or "'{}': '{}',\n"
        end_multinostr = notrail and "'{}': {}\n" or "'{}': {},\n"

        if isinstance(content, dict):
            if content:
                if asignation:
                    self._write(tab_level, "{}={{\n".format(name))
                else:
                    self._write(tab_level, "'{}': {{\n".format(name))
                for f, v in content.items():
                    self._write_dictformater(tab_level + 1, f, v)
                self._write(tab_level, "},\n")
            else:
                self._write(tab_level, end_singleline.format(name))
        elif isinstance(content, str):
            self._write(tab_level, end_multistr.format(name, content))
        else:
            self._write(tab_level, end_multinostr.format(name, content))

    def _initial_creator(self, initial):
        tab_level = 1
        self._write(tab_level, "initial = {}\n".format(initial))

    def _depends_creator(self, depends):
        tab_level = 1
        self._write(tab_level, "depends = ['{}']\n".format("', '".join(depends)))

    def _actions_creator(self, actions):
        tab_level = 1
        self._write(tab_level, "actions = [\n")
        for action in actions:
            self._write(2, "{}(\n".format(action.__class__.__name__))
            self._write(3, "'{}',\n".format(action.model_name))
            self._write_dictformater(3, "fields", action.fields, asignation=True)
            self._write_dictformater(3, "meta", action.meta, asignation=True)
            self._write(2, "),\n")
        self._write(tab_level, "]\n")
