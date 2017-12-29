from asyncorm.models.migrations.migrator import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Author': {
                'meta': {
                    'unique_together': ('name', 'last_name'),
                    'table_name': '',
                    'ordering': None,
                },
                'fields': {
                    'age': {
                        'db_index': False,
                        'unique': False,
                        'db_column': 'age',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                    'id': {
                        'db_index': False,
                        'unique': True,
                        'db_column': 'id',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                    'email': {
                        'db_index': False,
                        'max_length': 100,
                        'unique': False,
                        'db_column': 'email',
                        'choices': None,
                        'default': None,
                        'null': True,
                    },
                    'name': {
                        'db_index': False,
                        'max_length': 50,
                        'unique': True,
                        'db_column': 'name',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                    'last_name': {
                        'db_index': False,
                        'max_length': 50,
                        'unique': True,
                        'db_column': 'last_name',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                },
            },
            'Book': {
                'meta': {
                    'unique_together': ['name', 'synopsis'],
                    'table_name': '',
                    'ordering': ['-name'],
                },
                'fields': {
                    'pages': {
                        'db_index': False,
                        'unique': False,
                        'db_column': 'pages',
                        'choices': None,
                        'default': None,
                        'null': True,
                    },
                    'book_type': {
                        'db_index': False,
                        'max_length': 15,
                        'unique': False,
                        'db_column': 'book_type',
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'default': None,
                        'null': True,
                    },
                    'id': {
                        'db_index': False,
                        'unique': True,
                        'db_column': 'id',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                    'synopsis': {
                        'db_index': False,
                        'max_length': 255,
                        'unique': False,
                        'db_column': 'synopsis',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                    'date_created': {
                        'auto_now': True,
                        'db_index': False,
                        'db_column': 'date_created',
                        'choices': None,
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                        'default': None,
                        'null': False,
                    },
                    'name': {
                        'db_index': False,
                        'max_length': 50,
                        'unique': False,
                        'db_column': 'name',
                        'choices': None,
                        'default': None,
                        'null': False,
                    },
                    'author': {
                        'foreign_key': 'Author',
                        'db_index': False,
                        'unique': False,
                        'default': None,
                        'db_column': 'author',
                    },
                },
            },
        }
