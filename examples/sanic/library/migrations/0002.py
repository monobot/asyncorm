from asyncorm.models.migrations.migration import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'meta': {},
                'fields': {
                    'pages': {
                        'default': None,
                        'null': True,
                        'unique': False,
                        'db_column': 'pages',
                        'choices': None,
                    },
                    'date_created': {
                        'strftime': '%Y-%m-%d',
                        'null': False,
                        'unique': False,
                        'db_column': 'date_created',
                        'choices': None,
                        'default': None,
                        'auto_now': True,
                    },
                    'book_type': {
                        'unique': False,
                        'null': True,
                        'max_length': 15,
                        'db_column': 'book_type',
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'default': None,
                    },
                    'id': {
                        'null': False,
                        'db_column': 'id',
                        'unique': True,
                    },
                    'name': {
                        'unique': False,
                        'null': False,
                        'max_length': 50,
                        'db_column': 'name',
                        'choices': None,
                        'default': None,
                    },
                    'synopsis': {
                        'unique': False,
                        'null': False,
                        'max_length': 255,
                        'db_column': 'synopsis',
                        'choices': None,
                        'default': None,
                    },
                },
            },
        }

