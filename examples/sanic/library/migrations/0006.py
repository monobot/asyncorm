from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'fields': {
                    'id': {
                        'db_column': 'id',
                        'default': None,
                        'db_index': False,
                        'null': False,
                        'unique': True,
                        'choices': None,
                    },
                    'email': {
                        'max_length': 100,
                        'db_column': 'email',
                        'default': None,
                        'null': True,
                        'db_index': False,
                        'unique': False,
                        'choices': None,
                    },
                    'name': {
                        'max_length': 50,
                        'db_column': 'name',
                        'default': None,
                        'null': False,
                        'db_index': False,
                        'unique': True,
                        'choices': None,
                    },
                    'last_name': {
                        'max_length': 50,
                        'db_column': 'last_name',
                        'default': None,
                        'null': False,
                        'db_index': False,
                        'unique': True,
                        'choices': None,
                    },
                    'age': {
                        'db_column': 'age',
                        'default': None,
                        'db_index': False,
                        'null': False,
                        'unique': False,
                        'choices': None,
                    },
                },
                'meta': {
                    'ordering': None,
                    'table_name': '',
                    'unique_together': ('name', 'last_name'),
                },
            },
            'Book': {
                'fields': {
                    'id': {
                        'db_column': 'id',
                        'default': None,
                        'db_index': False,
                        'null': False,
                        'unique': True,
                        'choices': None,
                    },
                    'name': {
                        'max_length': 50,
                        'db_column': 'name',
                        'default': None,
                        'null': False,
                        'db_index': False,
                        'unique': False,
                        'choices': None,
                    },
                    'date_created': {
                        'db_column': 'date_created',
                        'default': None,
                        'null': False,
                        'db_index': False,
                        'unique': False,
                        'choices': None,
                        'strftime': '%Y-%m-%d',
                        'auto_now': True,
                    },
                    'author': {
                        'db_column': 'author',
                        'default': None,
                        'foreign_key': 'Author',
                        'db_index': False,
                        'unique': False,
                    },
                    'pages': {
                        'db_column': 'pages',
                        'default': None,
                        'db_index': False,
                        'null': True,
                        'unique': False,
                        'choices': None,
                    },
                    'book_type': {
                        'max_length': 15,
                        'db_column': 'book_type',
                        'default': None,
                        'null': True,
                        'db_index': False,
                        'unique': False,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                    },
                    'synopsis': {
                        'max_length': 255,
                        'db_column': 'synopsis',
                        'default': None,
                        'null': False,
                        'db_index': False,
                        'unique': False,
                        'choices': None,
                    },
                },
                'meta': {
                    'ordering': ['-name'],
                    'table_name': '',
                    'unique_together': ['name', 'synopsis'],
                },
            },
        }
