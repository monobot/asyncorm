import asyncio
import unittest

from asyncorm.application import get_model, orm_app
from asyncorm.exceptions import *
from asyncorm.fields import *

Book = get_model('Book')

db_config = {
    'database': 'asyncorm',
    'host': 'localhost',
    'user': 'sanicdbuser',
    'password': 'sanicDbPass',
}


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


class ModuleTests(AioTestCase):

    def test_configuration(self):
        with self.assertRaises(ModuleError) as exc:
            get_model('Tato')
        self.assertTrue(
            'The model does not exists' in exc.exception.args[0]
        )

        # the orm is configure on the start of tests, but the data is kept
        self.assertEqual(
            orm_app.db_manager.conn_data['password'],
            db_config['password']
        )
        self.assertEqual(
            orm_app.db_manager.conn_data['database'],
            db_config['database']
        )

        # every model declared has the same db_manager
        self.assertTrue(orm_app.db_manager is Book.objects.db_manager)
