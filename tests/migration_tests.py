import asyncio
import unittest

from .testapp.models import Book
from asyncorm.migrations import Inspector


class AioTestCase(unittest.TestCase):

    # noinspection PyPep8Naming
    def __init__(self, methodName='runTest', loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self._function_cache = {}
        super(AioTestCase, self).__init__(methodName=methodName)

    def coroutine_function_decorator(self, func):
        def wrapper(*args, **kw):
            return self.loop.run_until_complete(func(*args, **kw))
        return wrapper

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if asyncio.iscoroutinefunction(attr):
            if item not in self._function_cache:
                self._function_cache[item] = self.coroutine_function_decorator(
                    attr
                )
            return self._function_cache[item]
        return attr


class MigrationTests(AioTestCase):

    def test_class__init__(self):
        dict_book = Inspector.jsonify(Book)

        # the inspector correctly retrieves the data
        self.assertEqual(dict_book['_table_name'], 'library')
        self.assertEqual(dict_book['_db_pk'], 'id')

        # even the data that comes from the metaclass
        self.assertEqual(dict_book['ordering'], ['-id'])
        self.assertEqual(dict_book['unique_together'], ['name', 'content'])
