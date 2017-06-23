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

    @staticmethod
    def tabulation(tab_level):
        if tab_level:
            return '    ' * tab_level
        return ''

    def init_creator(self):
        tab_level = 1
        self.write(tab_level, 'def __init__(self):\n')

    def attr_writer(self, name, value):
        tab_level = 2
        self.write(tab_level, 'self.' + name + ' = ' + value + '\n\n')

    def set_models(self, model_dict):
        self.attr_writer('models', str(model_dict))
