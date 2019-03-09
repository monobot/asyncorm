from tests.app_1.models import Book
from tests.test_helper import AioTestCase


class MigrationTests(AioTestCase):
    async def test_model_migrate(self):
        await Book.objects.create(**{"name": "chusco redondo", "content": "paperback"})
