from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'AsyncormMigrations': {
                'fields': {
                    'id': {
                        'null': False,
                        'choices': None,
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'db_index': False,
                    },
                    'name': {
                        'null': False,
                        'choices': None,
                        'db_column': 'name',
                        'unique': False,
                        'max_length': 75,
                        'default': None,
                        'db_index': False,
                    },
                    'applied': {
                        'null': False,
                        'strftime': '%Y-%m-%d',
                        'choices': None,
                        'db_column': 'applied',
                        'unique': False,
                        'auto_now': True,
                        'default': None,
                        'db_index': False,
                    },
                    'app': {
                        'null': False,
                        'choices': None,
                        'db_column': 'app',
                        'unique': False,
                        'max_length': 75,
                        'default': None,
                        'db_index': False,
                    },
                },
                'meta': {
                    'unique_together': [],
                    'table_name': 'asyncorm_migrations',
                    'ordering': ('-id',),
                },
            },
        }
