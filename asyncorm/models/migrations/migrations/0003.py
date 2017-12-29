from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'AsyncormMigrations': {
                'fields': {
                    'name': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'name',
                        'unique': False,
                        'db_index': False,
                        'max_length': 75,
                    },
                    'id': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'id',
                        'unique': True,
                        'db_index': False,
                    },
                    'app': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'app',
                        'unique': False,
                        'db_index': False,
                        'max_length': 75,
                    },
                    'applied': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'applied',
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                        'db_index': False,
                        'auto_now': True,
                    },
                },
                'meta': {
                    'ordering': ('-id',),
                    'unique_together': [],
                    'table_name': 'asyncorm_migrations',
                },
            },
        }
