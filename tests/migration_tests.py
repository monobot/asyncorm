from asyncorm.models import DecimalField

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
        field = DecimalField(**data)

        field.current_state()
        field.make_migration(data)

        data.update({'unique': True})
        field.make_migration(data)

    async def test_mdel_migrate(self):
        book = await Book.objects.create(
            **{'name': 'chusco redondo',
               'content': 'paperback'}
        )

        # print(book.migration_queries())
        book.migration_queries()
        book.make_migration()
