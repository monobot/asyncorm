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
                        'max_length': 75,
                        'unique': False,
                        'db_index': False,
                        'null': False,
                        'db_column': 'name',
                    },
                    'applied': {
                        'unique': False,
                        'default': None,
                        'null': False,
                        'choices': None,
                        'strftime': '%Y-%m-%d',
                        'db_index': False,
                        'auto_now': True,
                        'db_column': 'applied',
                    },
                    'app': {
                        'default': None,
                        'choices': None,
                        'max_length': 75,
                        'unique': False,
                        'db_index': False,
                        'null': False,
                        'db_column': 'app',
                    },
                    'id': {
                        'default': None,
                        'choices': None,
                        'unique': True,
                        'db_index': False,
                        'null': False,
                        'db_column': 'id',
                    },
                },
            },
        }
