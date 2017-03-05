import asyncio
import unittest

from asyncorm.application import configure_orm
from asyncorm.exceptions import *
from asyncorm.fields import *


db_config = {
    'database': 'asyncorm',
    'host': 'localhost',
    'user': 'sanicdbuser',
    'password': 'sanicDbPass',
}
orm_app = configure_orm({
    'db_config': db_config,
    'modules': ['tests.testapp', 'tests.testapp2'],
})
dm = orm_app.db_manager
loop = orm_app.loop

Publisher = orm_app.get_model('Publisher')
Book = orm_app.get_model('Book')
Author = orm_app.get_model('Author')
Organization = orm_app.get_model('Author')
Developer = orm_app.get_model('Developer')


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


class ModelTests(AioTestCase):

    def test_class__init__(self):
        # classmethods tests
        self.assertEqual(Book().table_name, 'library')
        self.assertEqual(Author().table_name, 'Author')

        fields = Book._get_fields()

        self.assertEqual(len(fields), 5)

        self.assertEqual(
            sorted(list(fields.keys())),
            sorted(['id', 'content', 'name', 'author', 'date_created'])
        )

    def test_instantiated__init__(self):
        # classmethods tests
        book = Book()

        self.assertEqual(book._db_pk, 'id')
        self.assertEqual(book._orm_pk, 'id')

        author = Author()

        self.assertEqual(author._db_pk, 'uid')
        self.assertEqual(author._orm_pk, 'na')

    def test__validate_kwargs(self):
        kwargs = {
            'name': 'name',
            'content': 3,
        }

        # raises the validate content has an incorrect value
        with self.assertRaises(FieldError) as exc:
            book = Book()
            book._validate_kwargs(kwargs)
        self.assertTrue(
            'is a wrong datatype for field' in exc.exception.args[0]
        )

        kwargs = {
            'id': 34,
            'name': 'name',
        }

        # also raises fielderror because you can not pre-set the object's id
        with self.assertRaises(FieldError) as exc:
            book = Book()
            book._validate_kwargs(kwargs)
        self.assertEqual(
            exc.exception.args[0],
            'Models can not be generated with forced id'
        )

        kwargs.pop('id')

        kwargs['volume'] = 23
        # raises the validate error because volume is not a correct attrib
        with self.assertRaises(ModelError) as exc:
            book = Book()
            book._validate_kwargs(kwargs)
        # its a list because we validate all kwargs
        self.assertEqual(
            exc.exception.args[0],
            ['"volume" is not an attribute for Book', ]
        )

        kwargs.pop('volume')

        # now it correctly validates
        book._validate_kwargs(kwargs)

    async def test_ordering(self):
        self.assertEqual(Book()._ordering, ['-id'])
        self.assertEqual(Author()._ordering, None)

        q_books = await Book.objects.filter(id__gt=10)
        self.assertEqual(q_books[-1].id, 11)
