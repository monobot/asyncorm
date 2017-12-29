from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'AsyncormMigrations': {
                'meta': {
                    'unique_together': [],
                    'ordering': ('-id',),
                    'table_name': 'asyncorm_migrations',
                },
                'fields': {
                    'id': {
                        'unique': True,
                        'null': False,
                        'db_index': False,
                        'db_column': 'id',
                        'default': None,
                        'choices': None,
                    },
                    'name': {
                        'unique': False,
                        'null': False,
                        'db_index': False,
                        'db_column': 'name',
                        'default': None,
                        'max_length': 75,
                        'choices': None,
                    },
                    'applied': {
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                        'null': False,
                        'db_index': False,
                        'db_column': 'applied',
                        'auto_now': True,
                        'default': None,
                        'choices': None,
                    },
                    'app': {
                        'unique': False,
                        'null': False,
                        'db_index': False,
                        'db_column': 'app',
                        'default': None,
                        'max_length': 75,
                        'choices': None,
                    },
                },
            },
        }
