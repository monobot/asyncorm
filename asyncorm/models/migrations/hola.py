from asyncorm.models.migrations.migration import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {'totorota': {'2': 1}}

