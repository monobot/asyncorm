from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'AsyncormMigrations': {
                'fields': {
                    'id': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'null': False,
                    },
                    'name': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'name',
                        'max_length': 75,
                        'unique': False,
                        'default': None,
                        'null': False,
                    },
                    'applied': {
                        'db_index': False,
                        'choices': None,
                        'auto_now': True,
                        'db_column': 'applied',
                        'unique': False,
                        'default': None,
                        'null': False,
                        'strftime': '%Y-%m-%d',
                    },
                    'app': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'app',
                        'max_length': 75,
                        'unique': False,
                        'default': None,
                        'null': False,
                    },
                },
                'meta': {
                    'table_name': 'asyncorm_migrations',
                    'ordering': ('-id',),
                    'unique_together': [],
                },
            },
        }
