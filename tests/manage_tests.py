from datetime import datetime
from datetime import timedelta

from asyncorm.exceptions import *
from asyncorm.fields import *

from .testapp.models import Author, Book
from .testapp2.models import Appointment
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

        with self.assertRaises(ModelDoesNotExist) as exc:
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

        async for book in Book.objects.all():
            pass

    async def test_filter(self):
        queryset = Book.objects.filter(id__lte=30)
        book = await queryset[0]

        self.assertTrue(isinstance(book, Book))
        self.assertTrue(await queryset.count() >= 20)

        queryset = Book.objects.filter(id__range=(280, 282))
        self.assertEqual(await queryset.count(), 1)

        # upside doesnt really makes sense but also works
        with self.assertRaises(QuerysetError) as exc:
            queryset = Book.objects.filter(id__range={282, 280})
        self.assertEqual(
            'range should be list or a tuple',
            exc.exception.args[0]
        )

        # upside doesnt really makes sense but also works
        queryset = Book.objects.filter(id__range=(282, 280))
        self.assertEqual(await queryset.count(), 0)

        # incorrect fitler tuple definition error catched
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id__range=(280, 234, 23))
        self.assertTrue(
            ('Not a correct tuple/list definition, ') in exc.exception.args[0])

        # incorrect fitler tuple definition error catched
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id__range=(280, ))
        self.assertTrue(
            ('should be of size 2') in exc.exception.args[0])

        # empty queryset
        queryset = Book.objects.filter(id__gt=2800)
        self.assertEqual(await queryset.count(), 0)

    async def test_comparisons_dates(self):
        today = datetime.now()
        await Appointment.objects.create(
            name='app1', date=today + timedelta(days=1)
        )
        await Appointment.objects.create(
            name='app2', date=today
        )
        await Appointment.objects.create(
            name='app3', date=today - timedelta(days=1)
        )

        self.assertEqual(
            await Appointment.objects.all().count(), 3)
        self.assertEqual(
            await Appointment.objects.filter(date__gt=today).count(),
            1
        )
        self.assertEqual(
            await Appointment.objects.filter(date__gte=today).count(),
            2
        )
        self.assertEqual(
            await Appointment.objects.filter(date__lt=today).count(),
            1
        )
        self.assertEqual(
            await Appointment.objects.filter(
                date__lte=today + timedelta(days=1)
            ).count(),
            3
        )

    async def test_in_lookup(self):
        queryset = Book.objects.filter(id__in=(1, 2, 56, 456))
        self.assertEqual(await queryset.count(), 3)

        queryset = Book.objects.filter(name__in=('1', '2', '56'))
        self.assertEqual(await queryset.count(), 0)

    async def test_string_lookups(self):
        with self.assertRaises(QuerysetError)as exc:
            queryset = Book.objects.filter(id__exact=3)
        self.assertEqual(
            'exact not allowed in non CharField fields',
            exc.exception.args[0]
        )

        queryset = Book.objects.filter(name__exact='book name 10')
        self.assertEqual(await queryset.count(), 1)

        queryset = Book.objects.filter(name__iexact='book NAME 10')
        self.assertEqual(await queryset.count(), 1)

        queryset = Book.objects.filter(name__iexact=' NAME 10')
        self.assertEqual(await queryset.count(), 0)

        queryset = Book.objects.filter(name__contains='NAME')
        self.assertEqual(await queryset.count(), 0)

        queryset = Book.objects.filter(name__icontains='NAME')
        self.assertTrue(await queryset.count() > 200)

        queryset = Book.objects.filter(name__startswith='book name 10')
        self.assertEqual(await queryset.count(), 11)

        queryset = Book.objects.filter(name__istartswith='boOk NAMe')
        self.assertTrue(await queryset.count() > 200)

        queryset = Book.objects.filter(name__endswith='name 51')
        self.assertEqual(await queryset.count(), 1)

        queryset = Book.objects.filter(name__iendswith='NAMe 23')
        self.assertEqual(await queryset.count(), 1)

    async def test_regex_lookups(self):
        q_book = Book.objects.filter(name__iregex='^book name 1$')
        self.assertEqual(await q_book.count(), 1)

        await Book.objects.get(name__iregex='^book NAME 1$')

        q_book = Book.objects.filter(name__iregex='^[b] NAME 1$')
        self.assertEqual(await q_book.count(), 0)

        q_book = Book.objects.filter(name__regex='^[b]')
        self.assertTrue(await q_book.count() > 200)

        q_book = Book.objects.filter(name__iregex='^[bhuijki]')
        self.assertTrue(await q_book.count() > 200)

    async def test_exclude(self):
        queryset = Book.objects.exclude(id__gt=280)

        book = await queryset[0]
        self.assertTrue(isinstance(book, Book))

        self.assertTrue(await queryset.count() >= 20)

        queryset = Book.objects.exclude(id__range=(280, 282))
        self.assertTrue(await queryset.count() > 250)

        # empty queryset
        queryset = Book.objects.exclude(id__lt=2800)
        self.assertEqual(await queryset.count(), 0)

    async def test_get(self):
        book = await Book.objects.get(id=280)

        self.assertTrue(isinstance(book, Book))

        # now try to get using wrong arguments (more than one)
        with self.assertRaises(MultipleObjectsReturned) as exc:
            await Book.objects.get(id__gt=280)
        self.assertTrue(
            'More than one Book where returned, there are' in
            exc.exception.args[0]
        )

        # now try to get using wrong arguments (no object)
        with self.assertRaises(ModelDoesNotExist) as exc:
            await Book.objects.get(id=2800)
        self.assertTrue('does not exist' in exc.exception.args[0])

    async def test_create(self):
        author = await Author.objects.create(**{'name': 'Juanito', 'age': 73})

        self.assertTrue(isinstance(author, Author))

    async def test_get_or_create(self):
        kwargs = {'name': 'Raulito', 'age': 73}
        author, created = await Author.objects.get_or_create(**kwargs)

        self.assertTrue(isinstance(author, Author))
        self.assertTrue(created)

        author, created = await Author.objects.get_or_create(**kwargs)
        self.assertTrue(isinstance(author, Author))
        self.assertFalse(created)
