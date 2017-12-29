from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'meta': {
                    'table_name': '',
                    'ordering': ['-name'],
                    'unique_together': ['name', 'synopsis'],
                },
                'fields': {
                    'name': {
                        'default': None,
                        'choices': None,
                        'max_length': 50,
                        'unique': False,
                        'db_index': False,
                        'null': False,
                        'db_column': 'name',
                    },
                    'date_created': {
                        'unique': False,
                        'default': None,
                        'null': False,
                        'choices': None,
                        'strftime': '%Y-%m-%d',
                        'db_index': False,
                        'auto_now': True,
                        'db_column': 'date_created',
                    },
                    'author': {
                        'foreign_key': 'Author',
                        'db_index': False,
                        'unique': False,
                        'default': None,
                        'db_column': 'author',
                    },
                    'synopsis': {
                        'default': None,
                        'choices': None,
                        'max_length': 255,
                        'unique': False,
                        'db_index': False,
                        'null': False,
                        'db_column': 'synopsis',
                    },
                    'id': {
                        'default': None,
                        'choices': None,
                        'unique': True,
                        'db_index': False,
                        'null': False,
                        'db_column': 'id',
                    },
                    'book_type': {
                        'default': None,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'max_length': 15,
                        'unique': False,
                        'db_index': False,
                        'null': True,
                        'db_column': 'book_type',
                    },
                    'pages': {
                        'default': None,
                        'choices': None,
                        'unique': False,
                        'db_index': False,
                        'null': True,
                        'db_column': 'pages',
                    },
                },
            },
            'Author': {
                'meta': {
                    'table_name': '',
                    'ordering': None,
                    'unique_together': ('name', 'last_name'),
                },
                'fields': {
                    'email': {
                        'default': None,
                        'choices': None,
                        'max_length': 100,
                        'unique': False,
                        'db_index': False,
                        'null': True,
                        'db_column': 'email',
                    },
                    'id': {
                        'default': None,
                        'choices': None,
                        'unique': True,
                        'db_index': False,
                        'null': False,
                        'db_column': 'id',
                    },
                    'age': {
                        'default': None,
                        'choices': None,
                        'unique': False,
                        'db_index': False,
                        'null': False,
                        'db_column': 'age',
                    },
                    'last_name': {
                        'default': None,
                        'choices': None,
                        'max_length': 50,
                        'unique': True,
                        'db_index': False,
                        'null': False,
                        'db_column': 'last_name',
                    },
                    'name': {
                        'default': None,
                        'choices': None,
                        'max_length': 50,
                        'unique': True,
                        'db_index': False,
                        'null': False,
                        'db_column': 'name',
                    },
                },
            },
        }
