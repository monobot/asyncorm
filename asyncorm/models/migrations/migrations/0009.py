from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'AsyncormMigrations': {
                'meta': {
                    'unique_together': [],
                    'table_name': 'asyncorm_migrations',
                    'ordering': ('-id',),
                },
                'fields': {
                    'applied': {
                        'auto_now': True,
                        'db_index': False,
                        'db_column': 'applied',
                        'choices': None,
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                        'default': None,
                        'null': False,
                    },
                    'id': {
                        'db_index': False,
                        'unique': True,
                        'db_column': 'id',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                    'name': {
                        'db_index': False,
                        'max_length': 75,
                        'unique': False,
                        'db_column': 'name',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                    'app': {
                        'db_index': False,
                        'max_length': 75,
                        'unique': False,
                        'db_column': 'app',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                },
            },
        }
