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
                    'name': {
                        'db_column': 'name',
                        'max_length': 50,
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_index': False,
                    },
                    'id': {
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_index': False,
                    },
                    'age': {
                        'db_column': 'age',
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_index': False,
                    },
                    'email': {
                        'db_column': 'email',
                        'max_length': 100,
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': True,
                        'db_index': False,
                    },
                    'last_name': {
                        'db_column': 'last_name',
                        'max_length': 50,
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
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
                        'db_column': 'name',
                        'max_length': 50,
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_index': False,
                    },
                    'book_type': {
                        'db_column': 'book_type',
                        'max_length': 15,
                        'unique': False,
                        'default': None,
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'null': True,
                        'db_index': False,
                    },
                    'date_created': {
                        'db_column': 'date_created',
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                        'null': False,
                        'default': None,
                        'choices': None,
                        'auto_now': True,
                        'db_index': False,
                    },
                    'author': {
                        'db_column': 'author',
                        'default': None,
                        'unique': False,
                        'foreign_key': 'Author',
                        'db_index': False,
                    },
                    'id': {
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_index': False,
                    },
                    'synopsis': {
                        'db_column': 'synopsis',
                        'max_length': 255,
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': False,
                        'db_index': False,
                    },
                    'pages': {
                        'db_column': 'pages',
                        'unique': False,
                        'default': None,
                        'choices': None,
                        'null': True,
                        'db_index': False,
                    },
                },
            },
        }
