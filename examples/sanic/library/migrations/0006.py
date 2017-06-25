from asyncorm.models.migrations.migration import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'fields': {
                    'name': {
                        'db_column': 'name',
                        'choices': None,
                        'unique': False,
                        'default': None,
                        'null': False,
                        'max_length': 50,
                    },
                    'id': {
                        'db_column': 'id',
                        'null': False,
                        'unique': True,
                    },
                    'book_type': {
                        'db_column': 'book_type',
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'unique': False,
                        'default': None,
                        'null': True,
                        'max_length': 15,
                    },
                    'synopsis': {
                        'db_column': 'synopsis',
                        'choices': None,
                        'unique': False,
                        'default': None,
                        'null': False,
                        'max_length': 255,
                    },
                    'pages': {
                        'db_column': 'pages',
                        'default': None,
                        'unique': False,
                        'choices': None,
                        'null': True,
                    },
                    'date_created': {
                        'db_column': 'date_created',
                        'choices': None,
                        'strftime': '%Y-%m-%d',
                        'unique': False,
                        'default': None,
                        'null': False,
                        'auto_now': True,
                    },
                },
                'meta': {},
            },
        }

