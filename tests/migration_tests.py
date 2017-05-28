from asyncorm.migrations import Inspector
from asyncorm import fields

from .testapp.models import Book
from .test_helper import AioTestCase


class MigrationTests(AioTestCase):

    def test_class__init__(self):
        data = {
            'decimal_places': 2,
            'default': None,
            'max_digits': 10,
            'unique': False,
            'null': False,
            'db_column': '',
            'choices': None
        }
        field = fields.DecimalField(**data)

        # print(field.current_state())
        # print(field.make_migration(data))

        data.update({'unique': True})
        # print(field.make_migration(data))
