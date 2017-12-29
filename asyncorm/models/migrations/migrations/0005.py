from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'AsyncormMigrations': {
                'meta': {
                    'table_name': 'asyncorm_migrations',
                    'unique_together': [],
                    'ordering': ('-id',),
                },
                'fields': {
                    'name': {
                        'max_length': 75,
                        'default': None,
                        'db_index': False,
                        'db_column': 'name',
                        'choices': None,
                        'null': False,
                        'unique': False,
                    },
                    'app': {
                        'max_length': 75,
                        'default': None,
                        'db_index': False,
                        'db_column': 'app',
                        'choices': None,
                        'null': False,
                        'unique': False,
                    },
                    'id': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'id',
                        'choices': None,
                        'null': False,
                        'unique': True,
                    },
                    'applied': {
                        'default': None,
                        'strftime': '%Y-%m-%d',
                        'db_index': False,
                        'auto_now': True,
                        'db_column': 'applied',
                        'choices': None,
                        'null': False,
                        'unique': False,
                    },
                },
            },
        }
