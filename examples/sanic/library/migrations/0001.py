from asyncorm.models.migrations.migration import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'meta': {},
                'fields': {
                    'synopsis': {
                        'choices': None,
                        'default': None,
                        'null': False,
                        'unique': False,
                        'max_length': 255,
                        'db_column': 'synopsis',
                    },
                    'name': {
                        'choices': None,
                        'default': None,
                        'null': False,
                        'unique': False,
                        'max_length': 50,
                        'db_column': 'name',
                    },
                    'date_created': {
                        'auto_now': True,
                        'choices': None,
                        'default': None,
                        'null': False,
                        'unique': False,
                        'db_column': 'date_created',
                        'strftime': '%Y-%m-%d',
                    },
                    'book_type': {
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'default': None,
                        'null': True,
                        'unique': False,
                        'max_length': 15,
                        'db_column': 'book_type',
                    },
                    'id': {
                        'db_column': 'id',
                        'null': False,
                        'unique': True,
                    },
                    'pages': {
                        'choices': None,
                        'default': None,
                        'db_column': 'pages',
                        'null': True,
                        'unique': False,
                    },
                },
            },
        }

