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
                    'applied': {
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'applied',
                        'strftime': '%Y-%m-%d',
                        'auto_now': True,
                        'db_index': False,
                    },
                    'name': {
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'name',
                        'max_length': 75,
                        'db_index': False,
                    },
                    'id': {
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'id',
                        'db_index': False,
                    },
                    'app': {
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'app',
                        'max_length': 75,
                        'db_index': False,
                    },
                },
            },
        }
