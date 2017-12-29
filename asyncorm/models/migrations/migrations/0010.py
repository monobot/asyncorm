from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'AsyncormMigrations': {
                'fields': {
                    'applied': {
                        'unique': False,
                        'null': False,
                        'db_index': False,
                        'strftime': '%Y-%m-%d',
                        'choices': None,
                        'default': None,
                        'auto_now': True,
                        'db_column': 'applied',
                    },
                    'name': {
                        'unique': False,
                        'choices': None,
                        'max_length': 75,
                        'db_index': False,
                        'default': None,
                        'null': False,
                        'db_column': 'name',
                    },
                    'id': {
                        'unique': True,
                        'choices': None,
                        'db_index': False,
                        'null': False,
                        'default': None,
                        'db_column': 'id',
                    },
                    'app': {
                        'unique': False,
                        'choices': None,
                        'max_length': 75,
                        'db_index': False,
                        'default': None,
                        'null': False,
                        'db_column': 'app',
                    },
                },
                'meta': {
                    'unique_together': [],
                    'table_name': 'asyncorm_migrations',
                    'ordering': ('-id',),
                },
            },
        }
