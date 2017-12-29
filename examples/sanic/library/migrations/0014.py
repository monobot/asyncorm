from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'fields': {
                    'age': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'age',
                        'unique': False,
                        'default': None,
                        'null': False,
                    },
                    'id': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'null': False,
                    },
                    'name': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'name',
                        'max_length': 50,
                        'unique': True,
                        'default': None,
                        'null': False,
                    },
                    'email': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'email',
                        'max_length': 100,
                        'unique': False,
                        'default': None,
                        'null': True,
                    },
                    'last_name': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'last_name',
                        'max_length': 50,
                        'unique': True,
                        'default': None,
                        'null': False,
                    },
                },
                'meta': {
                    'table_name': '',
                    'ordering': None,
                    'unique_together': ('name', 'last_name'),
                },
            },
            'Book': {
                'fields': {
                    'id': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'id',
                        'unique': True,
                        'default': None,
                        'null': False,
                    },
                    'name': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'name',
                        'max_length': 50,
                        'unique': False,
                        'default': None,
                        'null': False,
                    },
                    'date_created': {
                        'db_index': False,
                        'choices': None,
                        'auto_now': True,
                        'db_column': 'date_created',
                        'unique': False,
                        'default': None,
                        'null': False,
                        'strftime': '%Y-%m-%d',
                    },
                    'book_type': {
                        'db_index': False,
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'db_column': 'book_type',
                        'max_length': 15,
                        'unique': False,
                        'default': None,
                        'null': True,
                    },
                    'author': {
                        'db_index': False,
                        'unique': False,
                        'default': None,
                        'foreign_key': 'Author',
                        'db_column': 'author',
                    },
                    'pages': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'pages',
                        'unique': False,
                        'default': None,
                        'null': True,
                    },
                    'synopsis': {
                        'db_index': False,
                        'choices': None,
                        'db_column': 'synopsis',
                        'max_length': 255,
                        'unique': False,
                        'default': None,
                        'null': False,
                    },
                },
                'meta': {
                    'table_name': '',
                    'ordering': ['-name'],
                    'unique_together': ['name', 'synopsis'],
                },
            },
        }
