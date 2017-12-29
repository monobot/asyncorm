from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'fields': {
                    'id': {
                        'unique': True,
                        'choices': None,
                        'db_index': False,
                        'null': False,
                        'default': None,
                        'db_column': 'id',
                    },
                    'name': {
                        'unique': True,
                        'choices': None,
                        'max_length': 50,
                        'db_index': False,
                        'default': None,
                        'null': False,
                        'db_column': 'name',
                    },
                    'age': {
                        'unique': False,
                        'choices': None,
                        'db_index': False,
                        'null': False,
                        'default': None,
                        'db_column': 'age',
                    },
                    'email': {
                        'unique': False,
                        'choices': None,
                        'max_length': 100,
                        'db_index': False,
                        'default': None,
                        'null': True,
                        'db_column': 'email',
                    },
                    'last_name': {
                        'unique': True,
                        'choices': None,
                        'max_length': 50,
                        'db_index': False,
                        'default': None,
                        'null': False,
                        'db_column': 'last_name',
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
                        'unique': False,
                        'choices': None,
                        'db_index': False,
                        'null': True,
                        'default': None,
                        'db_column': 'pages',
                    },
                    'author': {
                        'unique': False,
                        'foreign_key': 'Author',
                        'default': None,
                        'db_column': 'author',
                        'db_index': False,
                    },
                    'book_type': {
                        'unique': False,
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'max_length': 15,
                        'db_index': False,
                        'default': None,
                        'null': True,
                        'db_column': 'book_type',
                    },
                    'synopsis': {
                        'unique': False,
                        'choices': None,
                        'max_length': 255,
                        'db_index': False,
                        'default': None,
                        'null': False,
                        'db_column': 'synopsis',
                    },
                    'name': {
                        'unique': False,
                        'choices': None,
                        'max_length': 50,
                        'db_index': False,
                        'default': None,
                        'null': False,
                        'db_column': 'name',
                    },
                    'id': {
                        'unique': True,
                        'choices': None,
                        'db_index': False,
                        'null': False,
                        'default': None,
                        'db_column': 'id',
                    },
                    'date_created': {
                        'unique': False,
                        'null': False,
                        'db_index': False,
                        'strftime': '%Y-%m-%d',
                        'choices': None,
                        'default': None,
                        'auto_now': True,
                        'db_column': 'date_created',
                    },
                },
                'meta': {
                    'unique_together': ['name', 'synopsis'],
                    'table_name': '',
                    'ordering': ['-name'],
                },
            },
        }
