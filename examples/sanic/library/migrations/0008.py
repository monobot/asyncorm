from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'fields': {
                    'id': {
                        'null': False,
                        'choices': None,
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'db_index': False,
                    },
                    'email': {
                        'null': True,
                        'choices': None,
                        'db_column': 'email',
                        'unique': False,
                        'max_length': 100,
                        'default': None,
                        'db_index': False,
                    },
                    'name': {
                        'null': False,
                        'choices': None,
                        'db_column': 'name',
                        'unique': True,
                        'max_length': 50,
                        'default': None,
                        'db_index': False,
                    },
                    'last_name': {
                        'null': False,
                        'choices': None,
                        'db_column': 'last_name',
                        'unique': True,
                        'max_length': 50,
                        'default': None,
                        'db_index': False,
                    },
                    'age': {
                        'null': False,
                        'choices': None,
                        'db_column': 'age',
                        'unique': False,
                        'default': None,
                        'db_index': False,
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
                    'pages': {
                        'null': True,
                        'choices': None,
                        'db_column': 'pages',
                        'unique': False,
                        'default': None,
                        'db_index': False,
                    },
                    'name': {
                        'null': False,
                        'choices': None,
                        'db_column': 'name',
                        'unique': False,
                        'max_length': 50,
                        'default': None,
                        'db_index': False,
                    },
                    'date_created': {
                        'null': False,
                        'strftime': '%Y-%m-%d',
                        'choices': None,
                        'db_column': 'date_created',
                        'unique': False,
                        'auto_now': True,
                        'default': None,
                        'db_index': False,
                    },
                    'id': {
                        'null': False,
                        'choices': None,
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'db_index': False,
                    },
                    'author': {
                        'unique': False,
                        'default': None,
                        'db_index': False,
                        'db_column': 'author',
                        'foreign_key': 'Author',
                    },
                    'book_type': {
                        'null': True,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'db_column': 'book_type',
                        'unique': False,
                        'max_length': 15,
                        'default': None,
                        'db_index': False,
                    },
                    'synopsis': {
                        'null': False,
                        'choices': None,
                        'db_column': 'synopsis',
                        'unique': False,
                        'max_length': 255,
                        'default': None,
                        'db_index': False,
                    },
                },
                'meta': {
                    'unique_together': ['name', 'synopsis'],
                    'table_name': '',
                    'ordering': ['-name'],
                },
            },
        }
