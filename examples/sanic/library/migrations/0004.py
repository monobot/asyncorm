from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'fields': {
                    'synopsis': {
                        'default': None,
                        'db_index': False,
                        'max_length': 255,
                        'choices': None,
                        'unique': False,
                        'db_column': 'synopsis',
                        'null': False,
                    },
                    'name': {
                        'default': None,
                        'db_index': False,
                        'max_length': 50,
                        'choices': None,
                        'unique': False,
                        'db_column': 'name',
                        'null': False,
                    },
                    'id': {
                        'default': None,
                        'db_index': False,
                        'choices': None,
                        'unique': True,
                        'db_column': 'id',
                        'null': False,
                    },
                    'pages': {
                        'default': None,
                        'db_index': False,
                        'choices': None,
                        'unique': False,
                        'db_column': 'pages',
                        'null': True,
                    },
                    'date_created': {
                        'default': None,
                        'db_index': False,
                        'strftime': '%Y-%m-%d',
                        'auto_now': True,
                        'null': False,
                        'unique': False,
                        'db_column': 'date_created',
                        'choices': None,
                    },
                    'book_type': {
                        'default': None,
                        'db_index': False,
                        'max_length': 15,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'unique': False,
                        'db_column': 'book_type',
                        'null': True,
                    },
                    'author': {
                        'foreign_key': 'Author',
                        'default': None,
                        'db_index': False,
                        'db_column': 'author',
                        'unique': False,
                    },
                },
                'meta': {
                    'unique_together': ['name', 'synopsis'],
                    'ordering': ['-name'],
                    'table_name': '',
                },
            },
            'Author': {
                'fields': {
                    'last_name': {
                        'default': None,
                        'db_index': False,
                        'max_length': 50,
                        'choices': None,
                        'unique': True,
                        'db_column': 'last_name',
                        'null': False,
                    },
                    'name': {
                        'default': None,
                        'db_index': False,
                        'max_length': 50,
                        'choices': None,
                        'unique': True,
                        'db_column': 'name',
                        'null': False,
                    },
                    'age': {
                        'default': None,
                        'db_index': False,
                        'choices': None,
                        'unique': False,
                        'db_column': 'age',
                        'null': False,
                    },
                    'id': {
                        'default': None,
                        'db_index': False,
                        'choices': None,
                        'unique': True,
                        'db_column': 'id',
                        'null': False,
                    },
                    'email': {
                        'default': None,
                        'db_index': False,
                        'max_length': 100,
                        'choices': None,
                        'unique': False,
                        'db_column': 'email',
                        'null': True,
                    },
                },
                'meta': {
                    'unique_together': ('name', 'last_name'),
                    'ordering': None,
                    'table_name': '',
                },
            },
        }
