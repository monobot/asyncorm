from asyncorm.models import DecimalField

from .testapp.models import Book
from .test_helper import AioTestCase


class MigrationTests(AioTestCase):

    async def test_model_migrate(self):
        book = await Book.objects.create(
            **{'name': 'chusco redondo',
               'content': 'paperback'}
        )

        # print(book.migration_queries())
        # book.migration_queries()
        # await book.make_migration()
