from asyncorm.models.migrations.migration import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'fields': {
                    'book_type': {
                        'null': True,
                        'default': None,
                        'max_length': 15,
                        'choices': {
                            'hard cover': 'hard cover book',
                            'paperback': 'paperback book',
                        },
                        'unique': False,
                        'db_column': 'book_type',
                    },
                    'name': {
                        'null': False,
                        'default': None,
                        'max_length': 50,
                        'choices': None,
                        'unique': False,
                        'db_column': 'name',
                    },
                    'pages': {
                        'choices': None,
                        'null': True,
                        'db_column': 'pages',
                        'unique': False,
                        'default': None,
                    },
                    'id': {
                        'null': False,
                        'db_column': 'id',
                        'unique': True,
                    },
                    'date_created': {
                        'auto_now': True,
                        'default': None,
                        'null': False,
                        'db_column': 'date_created',
                        'choices': None,
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                    },
                    'synopsis': {
                        'null': False,
                        'default': None,
                        'max_length': 255,
                        'choices': None,
                        'unique': False,
                        'db_column': 'synopsis',
                    },
                },
                'meta': {},
            },
        }

