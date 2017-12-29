from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'meta': {
                    'table_name': '',
                    'unique_together': ('name', 'last_name'),
                    'ordering': None,
                },
                'fields': {
                    'name': {
                        'max_length': 50,
                        'default': None,
                        'db_index': False,
                        'db_column': 'name',
                        'choices': None,
                        'null': False,
                        'unique': True,
                    },
                    'last_name': {
                        'max_length': 50,
                        'default': None,
                        'db_index': False,
                        'db_column': 'last_name',
                        'choices': None,
                        'null': False,
                        'unique': True,
                    },
                    'email': {
                        'max_length': 100,
                        'default': None,
                        'db_index': False,
                        'db_column': 'email',
                        'choices': None,
                        'null': True,
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
                    'age': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'age',
                        'choices': None,
                        'null': False,
                        'unique': False,
                    },
                },
            },
            'Book': {
                'meta': {
                    'table_name': '',
                    'unique_together': ['name', 'synopsis'],
                    'ordering': ['-name'],
                },
                'fields': {
                    'name': {
                        'max_length': 50,
                        'default': None,
                        'db_index': False,
                        'db_column': 'name',
                        'choices': None,
                        'null': False,
                        'unique': False,
                    },
                    'pages': {
                        'default': None,
                        'db_index': False,
                        'db_column': 'pages',
                        'choices': None,
                        'null': True,
                        'unique': False,
                    },
                    'synopsis': {
                        'max_length': 255,
                        'default': None,
                        'db_index': False,
                        'db_column': 'synopsis',
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
                    'author': {
                        'db_column': 'author',
                        'default': None,
                        'unique': False,
                        'db_index': False,
                        'foreign_key': 'Author',
                    },
                    'book_type': {
                        'max_length': 15,
                        'default': None,
                        'db_index': False,
                        'db_column': 'book_type',
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'null': True,
                        'unique': False,
                    },
                    'date_created': {
                        'default': None,
                        'strftime': '%Y-%m-%d',
                        'db_index': False,
                        'auto_now': True,
                        'db_column': 'date_created',
                        'choices': None,
                        'null': False,
                        'unique': False,
                    },
                },
            },
        }
