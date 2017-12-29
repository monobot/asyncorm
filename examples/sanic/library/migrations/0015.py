from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'meta': {
                    'unique_together': ['name', 'synopsis'],
                    'ordering': ['-name'],
                    'table_name': '',
                },
                'fields': {
                    'date_created': {
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                        'null': False,
                        'db_index': False,
                        'db_column': 'date_created',
                        'auto_now': True,
                        'default': None,
                        'choices': None,
                    },
                    'author': {
                        'unique': False,
                        'foreign_key': 'Author',
                        'default': None,
                        'db_index': False,
                        'db_column': 'author',
                    },
                    'pages': {
                        'unique': False,
                        'null': True,
                        'db_index': False,
                        'db_column': 'pages',
                        'default': None,
                        'choices': None,
                    },
                    'book_type': {
                        'unique': False,
                        'null': True,
                        'db_index': False,
                        'db_column': 'book_type',
                        'default': None,
                        'max_length': 15,
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                    },
                    'name': {
                        'unique': False,
                        'null': False,
                        'db_index': False,
                        'db_column': 'name',
                        'default': None,
                        'max_length': 50,
                        'choices': None,
                    },
                    'synopsis': {
                        'unique': False,
                        'null': False,
                        'db_index': False,
                        'db_column': 'synopsis',
                        'default': None,
                        'max_length': 255,
                        'choices': None,
                    },
                    'id': {
                        'unique': True,
                        'null': False,
                        'db_index': False,
                        'db_column': 'id',
                        'default': None,
                        'choices': None,
                    },
                },
            },
            'Author': {
                'meta': {
                    'unique_together': ('name', 'last_name'),
                    'ordering': None,
                    'table_name': '',
                },
                'fields': {
                    'age': {
                        'unique': False,
                        'null': False,
                        'db_index': False,
                        'db_column': 'age',
                        'default': None,
                        'choices': None,
                    },
                    'id': {
                        'unique': True,
                        'null': False,
                        'db_index': False,
                        'db_column': 'id',
                        'default': None,
                        'choices': None,
                    },
                    'last_name': {
                        'unique': True,
                        'null': False,
                        'db_index': False,
                        'db_column': 'last_name',
                        'default': None,
                        'max_length': 50,
                        'choices': None,
                    },
                    'email': {
                        'unique': False,
                        'null': True,
                        'db_index': False,
                        'db_column': 'email',
                        'default': None,
                        'max_length': 100,
                        'choices': None,
                    },
                    'name': {
                        'unique': True,
                        'null': False,
                        'db_index': False,
                        'db_column': 'name',
                        'default': None,
                        'max_length': 50,
                        'choices': None,
                    },
                },
            },
        }
