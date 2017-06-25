from asyncorm.models.migrations.migration import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'fields': {
                    'id': {
                        'null': False,
                        'db_column': 'id',
                        'unique': True,
                    },
                    'pages': {
                        'null': True,
                        'choices': None,
                        'default': None,
                        'db_column': 'pages',
                        'unique': False,
                    },
                    'synopsis': {
                        'null': False,
                        'default': None,
                        'choices': None,
                        'db_column': 'synopsis',
                        'max_length': 255,
                        'unique': False,
                    },
                    'name': {
                        'null': False,
                        'default': None,
                        'choices': None,
                        'db_column': 'name',
                        'max_length': 50,
                        'unique': False,
                    },
                    'date_created': {
                        'null': False,
                        'auto_now': True,
                        'default': None,
                        'choices': None,
                        'db_column': 'date_created',
                        'strftime': '%Y-%m-%d',
                        'unique': False,
                    },
                    'book_type': {
                        'null': True,
                        'default': None,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'db_column': 'book_type',
                        'max_length': 15,
                        'unique': False,
                    },
                },
                'meta': {},
            },
        }

