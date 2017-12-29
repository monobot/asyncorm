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
                    'last_name': {
                        'db_index': False,
                        'db_column': 'last_name',
                        'unique': True,
                        'default': None,
                        'null': False,
                        'choices': None,
                        'max_length': 50,
                    },
                    'name': {
                        'db_index': False,
                        'db_column': 'name',
                        'unique': True,
                        'default': None,
                        'null': False,
                        'choices': None,
                        'max_length': 50,
                    },
                    'email': {
                        'db_index': False,
                        'db_column': 'email',
                        'unique': False,
                        'default': None,
                        'null': True,
                        'choices': None,
                        'max_length': 100,
                    },
                    'id': {
                        'db_index': False,
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'null': False,
                        'choices': None,
                    },
                    'age': {
                        'db_index': False,
                        'db_column': 'age',
                        'unique': False,
                        'default': None,
                        'null': False,
                        'choices': None,
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
                    'synopsis': {
                        'db_index': False,
                        'db_column': 'synopsis',
                        'unique': False,
                        'default': None,
                        'null': False,
                        'choices': None,
                        'max_length': 255,
                    },
                    'author': {
                        'db_index': False,
                        'foreign_key': 'Author',
                        'db_column': 'author',
                        'unique': False,
                        'default': None,
                    },
                    'pages': {
                        'db_index': False,
                        'db_column': 'pages',
                        'unique': False,
                        'default': None,
                        'null': True,
                        'choices': None,
                    },
                    'name': {
                        'db_index': False,
                        'db_column': 'name',
                        'unique': False,
                        'default': None,
                        'null': False,
                        'choices': None,
                        'max_length': 50,
                    },
                    'book_type': {
                        'db_index': False,
                        'db_column': 'book_type',
                        'unique': False,
                        'default': None,
                        'null': True,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'max_length': 15,
                    },
                    'id': {
                        'db_index': False,
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'null': False,
                        'choices': None,
                    },
                    'date_created': {
                        'db_index': False,
                        'db_column': 'date_created',
                        'unique': False,
                        'default': None,
                        'null': False,
                        'choices': None,
                        'auto_now': True,
                        'strftime': '%Y-%m-%d',
                    },
                },
            },
        }
