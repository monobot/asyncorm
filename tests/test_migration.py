from tests.app_1.models import Book
from asyncorm.test_case import AsyncormTestCase


class MigrationTests(AsyncormTestCase):
    async def test_model_migrate(self):
        await Book.objects.create(**{"name": "chusco redondo", "content": "paperback"})
