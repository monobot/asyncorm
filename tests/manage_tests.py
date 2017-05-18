from datetime import datetime

from asyncorm.exceptions import *
from asyncorm.fields import *

from .testapp.models import Author, Book
from .test_helper import AioTestCase


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
        book = await Book.objects.all()[5]

        await book.delete()
        with self.assertRaises(ModelError) as exc:
            await book.save()
        self.assertTrue('has already been deleted!' in exc.exception.args[0])

        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(**{'id': book.id})
        self.assertTrue('does not exist' in exc.exception.args[0])

    async def test_count(self):
        queryset = Book.objects.filter(id__lte=100)
        self.assertTrue(await queryset.count() == 100)

    async def test_filter_changed_fieldname(self):
        author = await Author.objects.filter(na__lt=5)[0]
        self.assertTrue(isinstance(author, Author))
        self.assertEqual(author.na, 1)

    async def test_slice(self):
        book = await Book.objects.filter(id__lt=25)[1]
        self.assertTrue(isinstance(book, Book))
        self.assertEqual(book.id, 23)

        q_book = Book.objects.filter(id__lt=5)
        with self.assertRaises(IndexError) as exc:
            book = await q_book[7]
        self.assertTrue(
            'index does not exist' in exc.exception.args[0]
        )

        queryset = await Book.objects.filter(id__lt=25)[5:]

        # you can iterate over the results
        async for itm in queryset:
            self.assertTrue(isinstance(itm, Book))
            # I check that the first one is 19, because:
            # id__lt=25 is id=1 to id=24, sorted -id, sliced [5:]
            self.assertEqual(itm.id, 24 - 5)
            break
        # or slice again the retrieve the index object
        book = await queryset[0]
        self.assertFalse(book.id == 24 - 5)

        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.filter(id__lte=30)[1: 2: 4]
        self.assertTrue(
            'step on Queryset is not allowed' == exc.exception.args[0]
        )

        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.filter(id__lte=30)[-1]
        self.assertTrue(
            'Negative indices are not allowed' == exc.exception.args[0]
        )

        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.filter(id__lte=30)[:-1]
        self.assertTrue(
            'Negative indices are not allowed' == exc.exception.args[0]
        )

        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.filter(id__lte=30)[-3:]
        self.assertTrue(
            'Negative indices are not allowed' == exc.exception.args[0]
        )

    async def test_filter(self):
        queryset = Book.objects.filter(id__lte=30)
        book = await queryset[0]

        self.assertTrue(isinstance(book, Book))
        self.assertTrue(await queryset.count() >= 20)

        queryset = Book.objects.filter(id=(280, 282))
        self.assertEqual(await queryset.count(), 1)

        # upside doesnt really makes sense but also works
        queryset = Book.objects.filter(id=(282, 280))
        self.assertEqual(await queryset.count(), 0)

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
        queryset = Book.objects.filter(id__gt=2800)
        self.assertEqual(await queryset.count(), 0)

    async def test_exclude(self):
        queryset = Book.objects.exclude(id__gt=280)

        book = await queryset[0]
        self.assertTrue(isinstance(book, Book))

        self.assertTrue(await queryset.count() >= 20)

        queryset = Book.objects.exclude(id=(280, 282))
        self.assertTrue(await queryset.count() > 250)

        # empty queryset
        queryset = Book.objects.exclude(id__lt=2800)
        self.assertEqual(await queryset.count(), 0)

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
