from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'meta': {
                    'unique_together': ('name', 'last_name'),
                    'ordering': None,
                    'table_name': '',
                },
                'fields': {
                    'last_name': {
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'last_name',
                        'max_length': 50,
                        'db_index': False,
                    },
                    'email': {
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': True,
                        'db_column': 'email',
                        'max_length': 100,
                        'db_index': False,
                    },
                    'age': {
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'age',
                        'db_index': False,
                    },
                    'name': {
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'name',
                        'max_length': 50,
                        'db_index': False,
                    },
                    'id': {
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'id',
                        'db_index': False,
                    },
                },
            },
            'Book': {
                'meta': {
                    'unique_together': ['name', 'synopsis'],
                    'ordering': ['-name'],
                    'table_name': '',
                },
                'fields': {
                    'name': {
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'name',
                        'max_length': 50,
                        'db_index': False,
                    },
                    'synopsis': {
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'synopsis',
                        'max_length': 255,
                        'db_index': False,
                    },
                    'book_type': {
                        'unique': False,
                        'default': None,
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'null': True,
                        'db_column': 'book_type',
                        'max_length': 15,
                        'db_index': False,
                    },
                    'author': {
                        'db_column': 'author',
                        'default': None,
                        'unique': False,
                        'db_index': False,
                        'foreign_key': 'Author',
                    },
                    'date_created': {
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'date_created',
                        'strftime': '%Y-%m-%d',
                        'auto_now': True,
                        'db_index': False,
                    },
                    'id': {
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'id',
                        'db_index': False,
                    },
                    'pages': {
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': True,
                        'db_column': 'pages',
                        'db_index': False,
                    },
                },
            },
        }
