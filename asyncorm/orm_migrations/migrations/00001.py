from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'AsyncormMigrations': {
                'fields': {
                    'applied': {
                        'null': False,
                        'unique': False,
                        'auto_now': True,
                        'default': None,
                        'db_index': False,
                        'db_column': 'applied',
                        'choices': None,
                        'strftime': '%Y-%m-%d',
                    },
                    'name': {
                        'null': False,
                        'unique': False,
                        'default': None,
                        'db_index': False,
                        'db_column': 'name',
                        'choices': None,
                        'max_length': 75,
                    },
                    'id': {
                        'null': False,
                        'unique': True,
                        'default': None,
                        'db_index': False,
                        'db_column': 'id',
                        'choices': None,
                    },
                    'app': {
                        'null': False,
                        'unique': False,
                        'default': None,
                        'db_index': False,
                        'db_column': 'app',
                        'choices': None,
                        'max_length': 75,
                    },
                },
                'meta': {
                    'unique_together': [],
                    'ordering': ('-id',),
                    'table_name': 'asyncorm_migrations',
                },
            },
        }
