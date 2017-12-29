from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'fields': {
                    'last_name': {
                        'db_index': False,
                        'choices': None,
                        'null': False,
                        'db_column': 'last_name',
                        'default': None,
                        'max_length': 50,
                        'unique': True,
                    },
                    'id': {
                        'db_index': False,
                        'choices': None,
                        'null': False,
                        'db_column': 'id',
                        'default': None,
                        'unique': True,
                    },
                    'name': {
                        'db_index': False,
                        'choices': None,
                        'null': False,
                        'db_column': 'name',
                        'default': None,
                        'max_length': 50,
                        'unique': True,
                    },
                    'age': {
                        'db_index': False,
                        'choices': None,
                        'null': False,
                        'db_column': 'age',
                        'default': None,
                        'unique': False,
                    },
                    'email': {
                        'db_index': False,
                        'choices': None,
                        'null': True,
                        'db_column': 'email',
                        'default': None,
                        'max_length': 100,
                        'unique': False,
                    },
                },
                'meta': {
                    'unique_together': ('name', 'last_name'),
                    'ordering': None,
                    'table_name': '',
                },
            },
            'Book': {
                'fields': {
                    'id': {
                        'db_index': False,
                        'choices': None,
                        'null': False,
                        'db_column': 'id',
                        'default': None,
                        'unique': True,
                    },
                    'date_created': {
                        'db_index': False,
                        'choices': None,
                        'null': False,
                        'auto_now': True,
                        'db_column': 'date_created',
                        'default': None,
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                    },
                    'book_type': {
                        'db_index': False,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'null': True,
                        'db_column': 'book_type',
                        'default': None,
                        'max_length': 15,
                        'unique': False,
                    },
                    'author': {
                        'db_index': False,
                        'default': None,
                        'foreign_key': 'Author',
                        'unique': False,
                        'db_column': 'author',
                    },
                    'name': {
                        'db_index': False,
                        'choices': None,
                        'null': False,
                        'db_column': 'name',
                        'default': None,
                        'max_length': 50,
                        'unique': False,
                    },
                    'synopsis': {
                        'db_index': False,
                        'choices': None,
                        'null': False,
                        'db_column': 'synopsis',
                        'default': None,
                        'max_length': 255,
                        'unique': False,
                    },
                    'pages': {
                        'db_index': False,
                        'choices': None,
                        'null': True,
                        'db_column': 'pages',
                        'default': None,
                        'unique': False,
                    },
                },
                'meta': {
                    'unique_together': ['name', 'synopsis'],
                    'ordering': ['-name'],
                    'table_name': '',
                },
            },
        }
