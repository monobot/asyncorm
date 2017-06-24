from decimal import Decimal

TEMPLATE_TEXT = '''\
from asyncorm.models.migrations.migration import MigrationBase


'''


class MigrationConstructor(object):

    def __init__(self, file_name):
        self.file_name = file_name
        with open(self.file_name, 'w') as f:
            f.write(TEMPLATE_TEXT)

        self.write(0, 'class Migration(MigrationBase):\n\n')
        self.init_creator()

    def write(self, tab_level, txt):
        with open(self.file_name, 'a') as myfile:
            myfile.write(self.tabulation(tab_level) + txt)

    def write_dictformater(self, tab_level, name, content, notrail=False):
        end_singleline = notrail and '\'{}\': {{}}\n' or'\'{}\': {{}},\n'
        end_multistr = notrail and '\'{}\': \'{}\'\n' or '\'{}\': \'{}\',\n'
        end_multinostr = notrail and '\'{}\': {}\n' or '\'{}\': {},\n'

        isNone = content is None

        if isinstance(content, dict):
            if content:
                self.write(tab_level, '\'{}\': {{\n'.format(name))
                for f, v in content.items():
                    self.write_dictformater(tab_level + 1, f, v)
                self.write(tab_level, '},\n')
            else:
                self.write(tab_level, end_singleline.format(name))
        elif isinstance(content, str):
            self.write(
                tab_level, end_multistr.format(name, content)
            )
        elif isinstance(content, (bool, int, float, Decimal)) or isNone:
            self.write(
                tab_level, end_multinostr.format(name, content)
            )

    @staticmethod
    def tabulation(tab_level):
        if tab_level:
            return '    ' * tab_level
        return ''

    def init_creator(self):
        tab_level = 1
        self.write(tab_level, 'def __init__(self):\n')

    def set_models(self, models_dict):
        tab_level = 2
        self.write(tab_level, 'self.models = {\n')
        for model_name, model_dict in models_dict.items():
            self.write_dictformater(
                tab_level + 1,
                model_name,
                model_dict,
            )
        self.write(tab_level, '}\n\n')
