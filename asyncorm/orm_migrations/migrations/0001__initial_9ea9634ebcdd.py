from asyncorm.models.app_migrator import MigrationBase
from asyncorm.orm_migrations.migration_actions import *


class Migration(MigrationBase):
    initial = True
    depends = ['']
    actions = [
        CreateModel(
            'AsyncormMigrations',
            fields={
                'name': {
                    'choices': None,
                    'db_column': 'name',
                    'db_index': False,
                    'default': None,
                    'max_length': 75,
                    'null': False,
                    'unique': False,
                },
                'applied': {
                    'auto_now': True,
                    'choices': None,
                    'db_column': 'applied',
                    'db_index': False,
                    'default': None,
                    'null': False,
                    'strftime': '%Y-%m-%d  %H:%s',
                    'unique': False,
                },
                'id': {
                    'choices': None,
                    'db_column': 'id',
                    'db_index': False,
                    'default': None,
                    'null': False,
                    'unique': True,
                },
            },
            meta={
                'ordering': ('-id',),
                'unique_together': [],
                'table_name': 'asyncorm_migrations',
            },
        ),
    ]
