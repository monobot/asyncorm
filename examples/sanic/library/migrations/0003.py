from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'fields': {
                    'id': {
                        'db_index': False,
                        'unique': True,
                        'null': False,
                        'db_column': 'id',
                        'default': None,
                        'choices': None,
                    },
                    'name': {
                        'db_index': False,
                        'unique': True,
                        'null': False,
                        'default': None,
                        'db_column': 'name',
                        'choices': None,
                        'max_length': 50,
                    },
                    'email': {
                        'db_index': False,
                        'unique': False,
                        'null': True,
                        'default': None,
                        'db_column': 'email',
                        'choices': None,
                        'max_length': 100,
                    },
                    'age': {
                        'db_index': False,
                        'unique': False,
                        'null': False,
                        'db_column': 'age',
                        'default': None,
                        'choices': None,
                    },
                    'last_name': {
                        'db_index': False,
                        'unique': True,
                        'null': False,
                        'default': None,
                        'db_column': 'last_name',
                        'choices': None,
                        'max_length': 50,
                    },
                },
                'meta': {
                    'unique_together': ('name', 'last_name'),
                    'table_name': '',
                    'ordering': None,
                },
            },
            'Book': {
                'fields': {
                    'name': {
                        'db_index': False,
                        'unique': False,
                        'null': False,
                        'default': None,
                        'db_column': 'name',
                        'choices': None,
                        'max_length': 50,
                    },
                    'synopsis': {
                        'db_index': False,
                        'unique': False,
                        'null': False,
                        'default': None,
                        'db_column': 'synopsis',
                        'choices': None,
                        'max_length': 255,
                    },
                    'author': {
                        'foreign_key': 'Author',
                        'unique': False,
                        'default': None,
                        'db_column': 'author',
                        'db_index': False,
                    },
                    'pages': {
                        'db_index': False,
                        'unique': False,
                        'null': True,
                        'db_column': 'pages',
                        'default': None,
                        'choices': None,
                    },
                    'id': {
                        'db_index': False,
                        'unique': True,
                        'null': False,
                        'db_column': 'id',
                        'default': None,
                        'choices': None,
                    },
                    'date_created': {
                        'auto_now': True,
                        'db_index': False,
                        'unique': False,
                        'null': False,
                        'default': None,
                        'db_column': 'date_created',
                        'choices': None,
                        'strftime': '%Y-%m-%d',
                    },
                    'book_type': {
                        'db_index': False,
                        'unique': False,
                        'null': True,
                        'default': None,
                        'db_column': 'book_type',
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'max_length': 15,
                    },
                },
                'meta': {
                    'unique_together': ['name', 'synopsis'],
                    'table_name': '',
                    'ordering': ['-name'],
                },
            },
        }
