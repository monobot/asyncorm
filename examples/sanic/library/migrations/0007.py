from asyncorm.models.migrations.migration import MigrationBase


class Migration(MigrationBase):

    def __init__(self):
        self.models = {
            'Book': {
                'fields': {
                    'book_type': {
                        'default': None,
                        'unique': False,
                        'db_column': 'book_type',
                        'null': True,
                        'choices': {
                            'paperback': 'paperback book',
                            'hard cover': 'hard cover book',
                        },
                        'max_length': 15,
                    },
                    'date_created': {
                        'auto_now': True,
                        'default': None,
                        'unique': False,
                        'strftime': '%Y-%m-%d',
                        'db_column': 'date_created',
                        'null': False,
                        'choices': None,
                    },
                    'id': {
                        'db_column': 'id',
                        'null': False,
                        'unique': True,
                    },
                    'pages': {
                        'db_column': 'pages',
                        'default': None,
                        'choices': None,
                        'unique': False,
                        'null': True,
                    },
                    'synopsis': {
                        'default': None,
                        'unique': False,
                        'db_column': 'synopsis',
                        'null': False,
                        'choices': None,
                        'max_length': 255,
                    },
                    'name': {
                        'default': None,
                        'unique': False,
                        'db_column': 'name',
                        'null': False,
                        'choices': None,
                        'max_length': 50,
                    },
                },
                'meta': {},
            },
        }

