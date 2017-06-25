from asyncorm.models.migrations.migration import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'fields': {
                    'date_created': {
                        'db_column': 'date_created',
                        'default': None,
                        'strftime': '%Y-%m-%d',
                        'auto_now': True,
                        'null': False,
                        'unique': False,
                        'choices': None,
                    },
                    'name': {
                        'db_column': 'name',
                        'default': None,
                        'max_length': 50,
                        'null': False,
                        'unique': False,
                        'choices': None,
                    },
                    'synopsis': {
                        'db_column': 'synopsis',
                        'default': None,
                        'max_length': 255,
                        'null': False,
                        'unique': False,
                        'choices': None,
                    },
                    'pages': {
                        'db_column': 'pages',
                        'default': None,
                        'unique': False,
                        'choices': None,
                        'null': True,
                    },
                    'book_type': {
                        'db_column': 'book_type',
                        'default': None,
                        'max_length': 15,
                        'null': True,
                        'unique': False,
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                    },
                    'id': {
                        'db_column': 'id',
                        'unique': True,
                        'null': False,
                    },
                },
                'meta': {},
            },
        }

