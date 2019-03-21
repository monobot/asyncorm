from asyncorm.test_case import AsyncormTestCase
from tests.app_1.models import Book


class MigrationTests(AsyncormTestCase):
    async def test_model_migrate(self):
        await Book.objects.create(**{"name": "chusco redondo", "content": "paperback"})
