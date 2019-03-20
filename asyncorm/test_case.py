import asyncio
import os
import unittest

from asyncorm.application import configure_orm


class AsyncormTestCase(unittest.TestCase):
    _pool = None

    def setUp(self):
        # starts the transaction
        self._connection = self.orm_app.db_backend.get_sync_connection(loop=self.loop)
        self._test_transaction = self._connection.transaction()
        self.loop.run_until_complete(self._test_transaction.start())

    def tearDown(self):
        # revert the transaction
        self.loop.run_until_complete(self._test_transaction.rollback())

    def __init__(self, methodName="runTest", loop=None):
        config_file = os.path.join(os.getcwd(), "tests", "asyncorm.ini")
        self.orm_app = configure_orm(config_file)
        self.loop = loop or asyncio.get_event_loop()
        self._function_cache = {}

        super(AsyncormTestCase, self).__init__(methodName=methodName)

    def coroutine_function_decorator(self, func):
        def wrapper(*args, **kwargs):
            return self.loop.run_until_complete(func(*args, **kwargs))

        return wrapper

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if asyncio.iscoroutinefunction(attr):
            if item not in self._function_cache:
                self._function_cache[item] = self.coroutine_function_decorator(attr)
            return self._function_cache[item]
        return attr
