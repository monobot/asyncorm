from .testapp.models import Book
from asyncorm.migrations import Inspector
from .test_helper import AioTestCase


class MigrationTests(AioTestCase):

    def test_class__init__(self):
        dict_book = Inspector.jsonify(Book)

        # the inspector correctly retrieves the data
        self.assertEqual(dict_book['table_name'], 'library')
        self.assertEqual(dict_book['db_pk'], 'id')

        # even the data that comes from the metaclass
        self.assertEqual(dict_book['ordering'], ['-id'])
        self.assertEqual(dict_book['unique_together'], ['name', 'content'])
