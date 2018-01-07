from asyncorm.orm_migrations.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'meta': {
                    'unique_together': ['name', 'synopsis'],
                    'table_name': '',
                    'ordering': ['-name'],
                },
                'fields': {
                    'book_type': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'book_type',
                        'unique': False,
                        'null': True,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'max_length': 15,
                    },
                    'pages': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'pages',
                        'unique': False,
                        'null': True,
                        'choices': None,
                    },
                    'synopsis': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'synopsis',
                        'unique': False,
                        'null': False,
                        'choices': None,
                        'max_length': 255,
                    },
                    'author': {
                        'default': None,
                        'foreign_key': 'Author',
                        'db_index': False,
                        'db_column': 'author',
                        'unique': False,
                    },
                    'name': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'name',
                        'unique': False,
                        'null': False,
                        'choices': None,
                        'max_length': 50,
                    },
                    'date_created': {
                        'default': None,
                        'strftime': '%Y-%m-%d',
                        'db_index': False,
                        'db_column': 'date_created',
                        'unique': False,
                        'auto_now': True,
                        'null': False,
                        'choices': None,
                    },
                    'id': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'id',
                        'unique': True,
                        'null': False,
                        'choices': None,
                    },
                },
            },
            'Author': {
                'meta': {
                    'unique_together': ('name', 'last_name'),
                    'table_name': '',
                    'ordering': None,
                },
                'fields': {
                    'last_name': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'last_name',
                        'unique': True,
                        'null': False,
                        'choices': None,
                        'max_length': 50,
                    },
                    'email': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'email',
                        'unique': False,
                        'null': True,
                        'choices': None,
                        'max_length': 100,
                    },
                    'name': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'name',
                        'unique': True,
                        'null': False,
                        'choices': None,
                        'max_length': 50,
                    },
                    'age': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'age',
                        'unique': False,
                        'null': False,
                        'choices': None,
                    },
                    'id': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'id',
                        'unique': True,
                        'null': False,
                        'choices': None,
                    },
                },
            },
        }
