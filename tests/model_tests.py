import asyncio
import unittest

from asyncorm.application import get_model
from asyncorm.exceptions import *
from asyncorm.fields import *

from .testapp.models import Book, Author
from .testapp2.models import Developer, Client, Organization

Book2 = get_model('Book')
Author2 = get_model('Author')


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
        # no matter how you import them they are the same object
        self.assertTrue(Author is Author2)
        self.assertTrue(Book is Book2)

        self.assertEqual(Book().table_name(), 'library')
        self.assertEqual(Author().table_name(), 'Author')

        fields = Book._get_fields()

        self.assertEqual(len(fields), 5)
        self.assertEqual(
            sorted(list(fields.keys())),
            sorted(['id', 'content', 'name', 'author', 'date_created'])
        )

        fields = Author._get_fields()

        self.assertEqual(len(fields), 4)
        self.assertEqual(
            sorted(list(fields.keys())),
            sorted(['na', 'name', 'age', 'publisher'])
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
        self.assertEqual(Book().ordering, ['-id'])
        self.assertEqual(Author().ordering, None)

        q_books = await Book.objects.filter(id__gt=10)
        self.assertEqual(q_books[-1].id, 11)

    async def test_fk(self):
        # the inverse relation is correctly set
        self.assertTrue(hasattr(Developer, 'client_set'))

        # create a developer
        dev = Developer(name='developboy', age=24)
        await dev.save()
        # Assign a boss to it
        client = Client(name='devman', dev=dev.id)
        await client.save()

        # the client has the dev correctly set
        self.assertTrue(client.dev == client.id)

        # and the relation comes back
        # the method exists
        self.assertTrue(await dev.client_set())
        clients_returned = await dev.client_set()
        # and is correct
        self.assertTrue(clients_returned[0].id == dev.id)

    async def test_m2m(self):
        # the inverse relation is correctly set
        self.assertTrue(hasattr(Organization, 'developer_set'))

        # new organization
        org_list = []
        for x in range(1, 6):
            org = Organization(name='ong molona')
            await org.save()
            org_list.append(org.id)

        # create a developer
        dev = Developer(name='developer', age=55, org=org_list)
        await dev.save()

        # and the relation comes back
        # the method exists
        devs_returned = await org.developer_set()
        orgs_returned = await dev.organization_set()

        # and they are correct
        self.assertEqual(devs_returned[0].id, dev.id)

        # the first is 1
        self.assertEqual(orgs_returned[0].id, 1)
        # the last corresponds to the last added
        self.assertEqual(orgs_returned[-1].id, org.id)
