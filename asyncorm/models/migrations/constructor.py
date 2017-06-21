TEMPLATE_TEXT = '''\
from asyncorm.models.migrations.migration import MigrationBase


'''


class MigrationConstructor(object):

    def __init__(self, file_name):
        self.file_name = file_name
        with open(self.file_name, 'w') as f:
            f.write(TEMPLATE_TEXT)

        self.write('class Migration(MigrationBase):\n\n')
        self.init_creator()

    def write(self, txt):
        with open(self.file_name, 'a') as myfile:
            myfile.write(txt)

    @staticmethod
    def tabulation(tab_level):
        return '    ' * tab_level

    def init_creator(self):
        tab_level = 1
        self.write(
            self.tabulation(tab_level) + 'def __init__(self):\n')
        self.write(
            self.tabulation(tab_level + 1) + 'pass\n')
