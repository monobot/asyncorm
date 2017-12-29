from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'meta': {
                    'table_name': '',
                    'ordering': None,
                    'unique_together': ('name', 'last_name'),
                },
                'fields': {
                    'name': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'name',
                        'max_length': 50,
                        'db_index': False,
                        'unique': True,
                    },
                    'email': {
                        'default': None,
                        'choices': None,
                        'null': True,
                        'db_column': 'email',
                        'max_length': 100,
                        'db_index': False,
                        'unique': False,
                    },
                    'id': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'id',
                        'db_index': False,
                        'unique': True,
                    },
                    'age': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'age',
                        'db_index': False,
                        'unique': False,
                    },
                    'last_name': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'last_name',
                        'max_length': 50,
                        'db_index': False,
                        'unique': True,
                    },
                },
            },
            'Book': {
                'meta': {
                    'table_name': '',
                    'ordering': ['-name'],
                    'unique_together': ['name', 'synopsis'],
                },
                'fields': {
                    'date_created': {
                        'default': None,
                        'auto_now': True,
                        'strftime': '%Y-%m-%d',
                        'choices': None,
                        'null': False,
                        'db_column': 'date_created',
                        'db_index': False,
                        'unique': False,
                    },
                    'book_type': {
                        'default': None,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'null': True,
                        'db_column': 'book_type',
                        'max_length': 15,
                        'db_index': False,
                        'unique': False,
                    },
                    'synopsis': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'synopsis',
                        'max_length': 255,
                        'db_index': False,
                        'unique': False,
                    },
                    'name': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'name',
                        'max_length': 50,
                        'db_index': False,
                        'unique': False,
                    },
                    'pages': {
                        'default': None,
                        'choices': None,
                        'null': True,
                        'db_column': 'pages',
                        'db_index': False,
                        'unique': False,
                    },
                    'id': {
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_column': 'id',
                        'db_index': False,
                        'unique': True,
                    },
                    'author': {
                        'db_column': 'author',
                        'default': None,
                        'unique': False,
                        'db_index': False,
                        'foreign_key': 'Author',
                    },
                },
            },
        }
