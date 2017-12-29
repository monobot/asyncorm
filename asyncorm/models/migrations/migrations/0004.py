from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'AsyncormMigrations': {
                'meta': {
                    'table_name': 'asyncorm_migrations',
                    'ordering': ('-id',),
                    'unique_together': [],
                },
                'fields': {
                    'name': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'name',
                        'max_length': 75,
                        'db_index': False,
                        'unique': False,
                    },
                    'app': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'app',
                        'max_length': 75,
                        'db_index': False,
                        'unique': False,
                    },
                    'id': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'id',
                        'db_index': False,
                        'unique': True,
                    },
                    'applied': {
                        'default': None,
                        'auto_now': True,
                        'strftime': '%Y-%m-%d',
                        'choices': None,
                        'null': False,
                        'db_column': 'applied',
                        'db_index': False,
                        'unique': False,
                    },
                },
            },
        }
