import asyncio
import unittest

from datetime import datetime

from asyncorm.exceptions import *
from asyncorm.fields import *

from .testapp.models import Author, Book


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


class ManageTestMethods(AioTestCase):

    async def test_save(self):
        book = Book(**{
            'name': 'lord of the rings',
            'content': 'hard cover',
            'date_created': datetime.now(),
            # 'author': 1
        })
        self.assertFalse(book.id)

        await book.save()
        self.assertTrue(book.id)

        orig_id = book.id

        await book.save()
        self.assertEqual(orig_id, book.id)

        # we can not create new books with same name and content together
        book = Book(**{'name': 'book name 5', 'content': 'hard cover'})
        with self.assertRaises(ModelError) as exc:
            await book.save()
        self.assertTrue(
            'The model violates a unique constraint' == exc.exception.args[0]
        )

        # but when any of them are different there is no problem
        book.name = 'this is a new name'
        await book.save()

        # we can not create new books with same name and content together
        author = Author(**{'name': 'Mnemonic', 'age': 73})
        await author.save()

        # author name is unique, will raise an exception
        author2 = Author(**{'name': 'Mnemonic', 'age': 73})
        with self.assertRaises(ModelError) as exc:
            await author2.save()
        self.assertTrue(
            'The model violates a unique constraint' == exc.exception.args[0]
        )

        author2.name = 'different name'
        # now it can be correctly saved
        await author2.save()

    async def test_delete(self):
        books = await Book.objects.all()
        book = books[0]

        await book.delete()
        with self.assertRaises(ModelError) as exc:
            await book.save()
        self.assertTrue('has already been deleted!' in exc.exception.args[0])

        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(**{'id': book.id})
        self.assertTrue('does not exist' in exc.exception.args[0])

    async def test_all(self):
        queryset = await Book.objects.all()

        self.assertTrue(len(queryset) >= 250)
        self.assertTrue(isinstance(queryset[0], Book))

    async def test_filter(self):
        queryset = await Book.objects.filter(id__gt=280)

        self.assertTrue(len(queryset) >= 20)
        self.assertTrue(isinstance(queryset[0], Book))

        queryset = await Book.objects.filter(id=(280, 282))
        self.assertEqual(len(queryset), 1)

        # upside doesnt really makes sense but als works
        queryset = await Book.objects.filter(id=(282, 280))
        self.assertEqual(len(queryset), 0)

        # incorrect fitler tuple definition error catched
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id=(280, 234, 23))
        self.assertTrue(
            ('Not a correct tuple definition, filter '
             'only allows tuples of size 2') in exc.exception.args[0])

        # incorrect fitler tuple definition error catched
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id=(280, ))
        self.assertTrue(
            ('Not a correct tuple definition, filter '
             'only allows tuples of size 2') in exc.exception.args[0])

        # empty queryset
        queryset = await Book.objects.filter(id__gt=2800)
        self.assertEqual(len(queryset), 0)

    async def test_exclude(self):
        queryset = await Book.objects.exclude(id__gt=280)

        self.assertTrue(len(queryset) >= 20)
        self.assertTrue(isinstance(queryset[0], Book))

        queryset = await Book.objects.exclude(id=(280, 282))
        self.assertTrue(len(queryset) > 250)

        # empty queryset
        queryset = await Book.objects.exclude(id__lt=2800)
        self.assertEqual(len(queryset), 0)

    async def test_get(self):
        book = await Book.objects.get(id=280)

        self.assertTrue(isinstance(book, Book))

        # now try to get using wrong arguments (more than one)
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id__gt=280)
        self.assertTrue(
            'More than one Book where returned, there are' in
            exc.exception.args[0]
        )

        # now try to get using wrong arguments (no object)
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id=2800)
        self.assertTrue('does not exist' in exc.exception.args[0])


if __name__ == '__main__':
    unittest.main()
