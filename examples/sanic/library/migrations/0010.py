from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'fields': {
                    'name': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'name',
                        'unique': True,
                        'db_index': False,
                        'max_length': 50,
                    },
                    'age': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'age',
                        'unique': False,
                        'db_index': False,
                    },
                    'last_name': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'last_name',
                        'unique': True,
                        'db_index': False,
                        'max_length': 50,
                    },
                    'id': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'id',
                        'unique': True,
                        'db_index': False,
                    },
                    'email': {
                        'null': True,
                        'choices': None,
                        'default': None,
                        'db_column': 'email',
                        'unique': False,
                        'db_index': False,
                        'max_length': 100,
                    },
                },
                'meta': {
                    'ordering': None,
                    'unique_together': ('name', 'last_name'),
                    'table_name': '',
                },
            },
            'Book': {
                'fields': {
                    'author': {
                        'foreign_key': 'Author',
                        'db_index': False,
                        'default': None,
                        'db_column': 'author',
                        'unique': False,
                    },
                    'synopsis': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'synopsis',
                        'unique': False,
                        'db_index': False,
                        'max_length': 255,
                    },
                    'name': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'name',
                        'unique': False,
                        'db_index': False,
                        'max_length': 50,
                    },
                    'id': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'id',
                        'unique': True,
                        'db_index': False,
                    },
                    'pages': {
                        'null': True,
                        'choices': None,
                        'default': None,
                        'db_column': 'pages',
                        'unique': False,
                        'db_index': False,
                    },
                    'date_created': {
                        'null': False,
                        'choices': None,
                        'default': None,
                        'db_column': 'date_created',
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                        'db_index': False,
                        'auto_now': True,
                    },
                    'book_type': {
                        'null': True,
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'default': None,
                        'db_column': 'book_type',
                        'unique': False,
                        'db_index': False,
                        'max_length': 15,
                    },
                },
                'meta': {
                    'ordering': ['-name'],
                    'unique_together': ['name', 'synopsis'],
                    'table_name': '',
                },
            },
        }
