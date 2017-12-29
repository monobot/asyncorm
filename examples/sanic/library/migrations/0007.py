from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'fields': {
                    'synopsis': {
                        'choices': None,
                        'default': None,
                        'null': False,
                        'max_length': 255,
                        'db_column': 'synopsis',
                        'db_index': False,
                        'unique': False,
                    },
                    'id': {
                        'choices': None,
                        'default': None,
                        'null': False,
                        'db_column': 'id',
                        'db_index': False,
                        'unique': True,
                    },
                    'date_created': {
                        'choices': None,
                        'auto_now': True,
                        'null': False,
                        'default': None,
                        'db_column': 'date_created',
                        'strftime': '%Y-%m-%d',
                        'db_index': False,
                        'unique': False,
                    },
                    'author': {
                        'db_column': 'author',
                        'unique': False,
                        'db_index': False,
                        'foreign_key': 'Author',
                        'default': None,
                    },
                    'name': {
                        'choices': None,
                        'default': None,
                        'null': False,
                        'max_length': 50,
                        'db_column': 'name',
                        'db_index': False,
                        'unique': False,
                    },
                    'book_type': {
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'default': None,
                        'null': True,
                        'max_length': 15,
                        'db_column': 'book_type',
                        'db_index': False,
                        'unique': False,
                    },
                    'pages': {
                        'choices': None,
                        'default': None,
                        'null': True,
                        'db_column': 'pages',
                        'db_index': False,
                        'unique': False,
                    },
                },
                'meta': {
                    'table_name': '',
                    'ordering': ['-name'],
                    'unique_together': ['name', 'synopsis'],
                },
            },
            'Author': {
                'fields': {
                    'id': {
                        'choices': None,
                        'default': None,
                        'null': False,
                        'db_column': 'id',
                        'db_index': False,
                        'unique': True,
                    },
                    'email': {
                        'choices': None,
                        'default': None,
                        'null': True,
                        'max_length': 100,
                        'db_column': 'email',
                        'db_index': False,
                        'unique': False,
                    },
                    'last_name': {
                        'choices': None,
                        'default': None,
                        'null': False,
                        'max_length': 50,
                        'db_column': 'last_name',
                        'db_index': False,
                        'unique': True,
                    },
                    'age': {
                        'choices': None,
                        'default': None,
                        'null': False,
                        'db_column': 'age',
                        'db_index': False,
                        'unique': False,
                    },
                    'name': {
                        'choices': None,
                        'default': None,
                        'null': False,
                        'max_length': 50,
                        'db_column': 'name',
                        'db_index': False,
                        'unique': True,
                    },
                },
                'meta': {
                    'table_name': '',
                    'ordering': None,
                    'unique_together': ('name', 'last_name'),
                },
            },
        }
