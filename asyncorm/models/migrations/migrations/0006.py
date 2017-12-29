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
                    'name': {
                        'db_column': 'name',
                        'max_length': 75,
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_index': False,
                    },
                    'app': {
                        'db_column': 'app',
                        'max_length': 75,
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_index': False,
                    },
                    'id': {
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_index': False,
                    },
                    'applied': {
                        'db_column': 'applied',
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                        'null': False,
                        'default': None,
                        'choices': None,
                        'auto_now': True,
                        'db_index': False,
                    },
                },
            },
        }
