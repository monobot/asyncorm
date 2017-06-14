TEMPLATE_TEXT = '''
from asyncorm.models.migrations.migration import Migration, ModelState

'''


class MigrationCreator(object):

    def __init__(self, file_name):
        self.file_name = file_name

    def write(self, text):
        with open(self.file_name, 'a') as myfile:
            myfile.write(text)
