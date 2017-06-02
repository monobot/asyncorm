from datetime import datetime
from datetime import timedelta

from asyncorm.exceptions import (
    ModelError, ModelDoesNotExist, QuerysetError, MultipleObjectsReturned
)

from .testapp.models import Author, Book
from .testapp2.models import Appointment, Developer, Client
from .test_helper import AioTestCase


class ManageTestMethods(AioTestCase):

    async def test_save_no_id_before_save(self):
        book = Book(**{
            'name': 'lord of the rings',
            'content': 'hard cover',
            'date_created': datetime.now(),
        })
        id_before_save = book.id

        await book.save()

        self.assertFalse(id_before_save)
        self.assertTrue(book.id)

    async def test_id_persitent(self):
        book = Book(**{
            'name': 'silmarilion',
            'content': 'hard cover',
            'date_created': datetime.now(),
        })
        await book.save()
        orig_id = book.id

        await book.save()

        self.assertEqual(orig_id, book.id)

    async def test_unique_together(self):
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

    async def test_unique(self):
        author = Author(**{'name': 'Mnemonic', 'age': 73})
        await author.save()
        # author name is unique, will raise an exception
        author2 = Author(**{'name': 'Mnemonic', 'age': 73})

        with self.assertRaises(ModelError) as exc:
            await author2.save()

        self.assertTrue(
            'The model violates a unique constraint' == exc.exception.args[0]
        )

    async def test_delete_can_not_be_saved(self):
        book = await Book.objects.all()[5]

        await book.delete()
        with self.assertRaises(ModelError) as exc:
            await book.save()

        self.assertTrue('has already been deleted!' in exc.exception.args[0])

    async def test_delete_also_deletes_in_database(self):
        book = await Book.objects.all()[5]

        await book.delete()
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

    async def test_slice_correct(self):
        book = await Book.objects.filter(id__lt=25)[1]

        self.assertTrue(isinstance(book, Book))

        self.assertEqual(book.id, 23)

    async def test_slice_incorrect_index(self):
        q_book = Book.objects.filter(id__lt=5)

        with self.assertRaises(IndexError) as exc:
            await q_book[7]

        self.assertTrue(
            'index does not exist' in exc.exception.args[0]
        )

    async def test_slice_iterate_over(self):
        queryset = await Book.objects.filter(id__lt=25)[5:]

        # you can iterate over the results
        async for itm in queryset:
            self.assertTrue(isinstance(itm, Book))
            self.assertEqual(itm.id, 24 - 5)
            break
        # or slice again the retrieve the index object
            # I check that the first one is 19, because:
            # id__lt=25 is id=1 to id=24, sorted -id, sliced [5:]

    async def test_slice_first_item(self):
        queryset = await Book.objects.filter(id__lt=25)[5:]

        book = await queryset[0]

        self.assertFalse(book.id == 24 - 5)

    async def test_slice_wrong_slice(self):
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.filter(id__lte=30)[1: 2: 4]

        self.assertTrue(
            'step on Queryset is not allowed' == exc.exception.args[0]
        )

    async def test_slice_negative_slice(self):
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.filter(id__lte=30)[-1]

        self.assertTrue(
            'Negative indices are not allowed' == exc.exception.args[0]
        )

    async def test_slice_negative_slice_stop(self):
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.filter(id__lte=30)[:-1]

        self.assertTrue(
            'Negative indices are not allowed' == exc.exception.args[0]
        )

    async def test_slice_negative_slice_start(self):
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

    async def test_range(self):
        queryset = Book.objects.filter(id__range=(280, 282))

        self.assertEqual(await queryset.count(), 3)

    async def test_range_wrong_range(self):
        # upside doesnt really makes sense but also works
        with self.assertRaises(QuerysetError) as exc:
            Book.objects.filter(id__range={282, 280})

        self.assertEqual(
            'range should be list or a tuple',
            exc.exception.args[0]
        )

    async def test_range_upside_down(self):
        # upside doesnt really makes sense but also works
        queryset = Book.objects.filter(id__range=(282, 280))

        # bigger than 282 and lower than 200, of course does not exist
        self.assertEqual(await queryset.count(), 0)

    async def test_range_triple_tuple(self):
        # incorrect fitler tuple definition error catched
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id__range=(280, 234, 23))

        self.assertTrue(
            ('Not a correct tuple/list definition, ') in exc.exception.args[0])

    async def test_range_incorrect_tuple(self):
        # incorrect fitler tuple definition error catched
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id__range=(280, ))

        self.assertTrue(
            ('should be of size 2') in exc.exception.args[0])

    async def test_comparisons_dates(self):
        today = datetime.now()
        yesterday = today + timedelta(days=1)
        await Appointment.objects.create(
            name='app1', date=today + timedelta(days=1))
        await Appointment.objects.create(name='app2', date=today)
        await Appointment.objects.create(
            name='app3', date=today - timedelta(days=1))

        all_appointments = await Appointment.objects.all().count()
        gt_today = await Appointment.objects.filter(date__gt=today).count()
        gte_today = await Appointment.objects.filter(date__gte=today).count()
        lt_today = await Appointment.objects.filter(date__lt=today).count()
        yday = await Appointment.objects.filter(date__lte=yesterday).count()

        self.assertEqual(all_appointments, 3)
        self.assertEqual(gt_today, 1)
        self.assertEqual(gte_today, 2)
        self.assertEqual(lt_today, 1)
        self.assertEqual(yday, 3)

    async def test_in_lookup_integerfield(self):
        queryset = Book.objects.filter(id__in=(1, 2, 56, 456))

        self.assertEqual(await queryset.count(), 3)

    async def test_in_lookup_stringfield(self):
        queryset = Book.objects.filter(name__in=('1', '2', '56'))

        self.assertEqual(await queryset.count(), 0)

    async def test_string_lookups_wrong_fieldtype(self):
        with self.assertRaises(QuerysetError)as exc:
            Book.objects.filter(id__exact=3)
        self.assertEqual(
            'exact not allowed in non CharField fields',
            exc.exception.args[0]
        )

    async def test_string_lookups_exact(self):
        queryset = Book.objects.filter(name__exact='book name 10')

        self.assertEqual(await queryset.count(), 1)

    async def test_string_lookups_iexact(self):
        queryset = Book.objects.filter(name__iexact='book NAME 10')

        self.assertEqual(await queryset.count(), 1)

    async def test_string_lookups_iexact_wrong(self):
        queryset = Book.objects.filter(name__iexact=' NAME 10')

        self.assertEqual(await queryset.count(), 0)

    async def test_string_lookups_contains_wrong(self):
        queryset = Book.objects.filter(name__contains='NAME')

        self.assertEqual(await queryset.count(), 0)

    async def test_string_lookups_icontains(self):
        queryset = Book.objects.filter(name__icontains='NAME')

        self.assertTrue(await queryset.count() > 200)

    async def test_string_lookups_startswith(self):
        queryset = Book.objects.filter(name__startswith='book name 10')

        self.assertEqual(await queryset.count(), 11)

    async def test_string_lookups_istartswith(self):
        queryset = Book.objects.filter(name__istartswith='boOk NAMe')

        self.assertTrue(await queryset.count() > 200)

    async def test_string_lookups_endswith(self):
        queryset = Book.objects.filter(name__endswith='name 51')

        self.assertEqual(await queryset.count(), 1)

    async def test_string_lookups_iendswith(self):
        queryset = Book.objects.filter(name__iendswith='NAMe 23')

        self.assertEqual(await queryset.count(), 1)

    async def test_regex_lookups_iregex(self):
        q_book = Book.objects.filter(name__iregex='^book name 1$')

        book_count = await q_book.count()

        self.assertEqual(book_count, 1)

    async def test_regex_lookups_get_iregex(self):
        await Book.objects.get(name__iregex='^book NAME 1$')

    async def test_regex_lookups_iregex_empty(self):
        q_book = Book.objects.filter(name__iregex='^[b] NAME 1$')

        self.assertEqual(await q_book.count(), 0)

    async def test_regex_lookups_regex(self):
        q_book = Book.objects.filter(name__regex='^[b]')

        self.assertTrue(await q_book.count() > 200)

    async def test_exclude(self):
        queryset = Book.objects.exclude(id__gt=280)

        book = await queryset[0]

        self.assertTrue(isinstance(book, Book))
        self.assertTrue(await queryset.count() >= 20)

    async def test_exclude_range(self):
        queryset = Book.objects.exclude(id__range=(280, 282))

        self.assertTrue(await queryset.count() > 250)

    async def test_exclude_empty(self):
        queryset = Book.objects.exclude(id__lt=2800)

        self.assertEqual(await queryset.count(), 0)

    async def test_order_by_ascending(self):
        queryset = Book.objects.exclude(id__gt=280).order_by('id', 'name')

        book = await queryset[0]

        self.assertTrue(isinstance(book, Book))
        self.assertEqual(book.id, 1)

    async def test_order_by_descending(self):
        queryset = Book.objects.exclude(id__gt=280).order_by('-id', 'name')

        book = await queryset[0]

        self.assertTrue(isinstance(book, Book))
        self.assertEqual(book.id, 280)

    async def test_none(self):
        queryset = Book.objects.none().order_by('id', 'name')

        results = await queryset.count()

        self.assertEqual(results, 0)

    async def test_get_correct(self):
        book = await Book.objects.get(id=280)

        self.assertTrue(isinstance(book, Book))

    async def test_get_multiple_error(self):
        # now try to get using wrong arguments (more than one)
        with self.assertRaises(MultipleObjectsReturned) as exc:
            await Book.objects.get(id__gt=280)
        self.assertTrue(
            'More than one Book where returned, there are' in
            exc.exception.args[0]
        )

    async def test_get_no_exists_exception(self):
        # now try to get using wrong arguments (no object)
        with self.assertRaises(ModelDoesNotExist) as exc:
            await Book.objects.get(id=2800)
        self.assertTrue('does not exist' in exc.exception.args[0])

    async def test_create(self):
        create_dict = {'name': 'Juanito', 'age': 73}

        author = await Author.objects.create(**create_dict)

        self.assertTrue(isinstance(author, Author))
        self.assertTrue(isinstance(author.na, int))

    async def test_get_or_create_exists(self):
        kwargs = {'name': 'Raulito', 'age': 73}

        author, created = await Author.objects.get_or_create(**kwargs)

        self.assertTrue(isinstance(author, Author))
        self.assertTrue(created)

    async def test_get_or_create_created(self):
        kwargs = {'id': 73}
        book, created = await Book.objects.get_or_create(**kwargs)

        self.assertTrue(isinstance(book, Book))
        self.assertFalse(created)

    async def test_only_with_filter(self):
        q_books = Book.objects.filter(
            name__startswith='book name 10').only('name')

        async for book in q_books:
            self.assertTrue(book.name)
            self.assertTrue(book.id is None)

    async def test_only_with_get(self):
        q_books = Book.objects.only('name')

        book = await q_books.get(id=34)

        self.assertTrue(book.name)
        self.assertTrue(book.id is None)

    async def test_sum(self):
        q_books = Book.objects.filter(id__lt=100)

        quant = await q_books.count()
        total_price = await q_books.Sum('price')

        self.assertEqual(total_price, quant * 25)

    async def test_max(self):
        await Book.objects.create(
            **{'name': 'chancleta 2',
               'price': 35,
               'content': 'hard cover',
               }
        )
        q_books = Book.objects.all()

        max_price = await q_books.Max('price')
        self.assertEqual(max_price, 35)

    async def test_min(self):
        await Book.objects.create(
            **{'name': 'chancleta',
               'price': 15,
               'content': 'hard cover',
               }
        )
        q_books = Book.objects.all()

        min_price = await q_books.Min('price')
        self.assertEqual(min_price, 15)

    async def test_stddev(self):
        new_data = {
            'name': 'chancletas nuevas',
            'price': 15,
            'content': 'hard cover',
        }
        await Book.objects.create(**new_data)
        q_books = Book.objects.all()

        min_price = await q_books.StdDev('price')

        self.assertTrue(min_price)

    async def test_exists_true(self):
        resp = await Book.objects.filter(**{'name__icontains': 'nam'}).exists()
        self.assertTrue(resp)

    async def test_exists_false(self):
        resp = await Book.objects.filter(**{'id': 155625}).exists()

        self.assertFalse(resp)

    def test_select_related_wrong_field(self):
        field_name = 'toto__noto'
        with self.assertRaises(QuerysetError) as exc:
            Book.objects.select_related(field_name)

        self.assertEqual(
            '{} is not a {} attribute.'.format(
                field_name.split('__')[0],
                'Book'
            ),
            exc.exception.args[0]
        )

    def test_select_related_wrong_fieldtype(self):
        field_name = 'name'
        with self.assertRaises(QuerysetError) as exc:
            Book.objects.select_related(field_name)

        self.assertEqual(
            '{} is not a ForeignKey Field for {}.'.format(field_name, 'Book'),
            exc.exception.args[0]
        )

    async def test_select_related_fieldtype_null(self):
        field_name = 'author'

        book = await Book.objects.select_related(field_name).get(id=12)
        book2 = await Book.objects.get(id=13)

        # in both cases the author is None
        self.assertTrue(book.author is None)
        self.assertTrue(book2.author is None)

    async def test_select_related_fieldtype_exists(self):
        author = await Author.objects.create(
            **{'name': 'new author', 'age': 23}
        )
        book = await Book.objects.create(**{
            'name': 'book with author',
            'content': 'hard cover',
            'author': author.na,
        })

        book = await Book.objects.select_related('author').get(id=book.id)

        self.assertTrue(isinstance(book.author, Author))

    async def test_select_related_fieldtype_exists_get(self):
        author = await Author.objects.create(
            **{'name': 'new new author', 'age': 23}
        )
        book = await Book.objects.create(**{
            'name': 'book with author 2',
            'content': 'hard cover',
            'author': author.na,
        })

        book = await Book.objects.select_related('author').get(id=book.id)

        self.assertTrue(isinstance(book.author, Author))

    async def test_select_related_fieldtype_exists_filter(self):
        # get the last book id
        last_book = await Book.objects.all()[0]
        author = await Author.objects.create(
            **{'name': 'supernew author', 'age': 23}
        )
        # we create a number of books
        for x in range(10):
            new_data = {
                'name': 'book-author {}'.format(str(x)),
                'content': 'hard cover',
                'author': author.na,
            }
            book = await Book.objects.create(**new_data)
        q_books = Book.objects.select_related('author').filter(
            id__gt=last_book.id
        )

        async for book in q_books:
            # we check each of them has the author prepopulated
            self.assertTrue(isinstance(book.author, Author))

    async def test_select_related_multiple(self):
        # get the last book id
        appoinment = await Appointment.objects.create(
            name='totorota',
            date=datetime.now(),
        )
        dev = await Developer.objects.create(
            name='this is a developer',
            age=23,
        )
        n_c = await Client.objects.create(**{
            'name': 'awesome cl',
            'dev': dev.id,
            'appoinment': appoinment.id,
        })

        client = await Client.objects.select_related('dev', 'appoinment'
                                                     ).get(id=n_c.id)

        self.assertTrue(isinstance(client.dev, Developer))
        self.assertTrue(isinstance(client.appoinment, Appointment))

    async def test_double_queryset(self):
        q_books = Book.objects.filter(id__gt=220).order_by('id')
        q_books_excluded = q_books.exclude(id__range=(200, 250)).order_by('id')

        book_a = await q_books[0]
        book_b = await q_books_excluded[0]

        self.assertEqual(book_a.id, 221)
        self.assertEqual(book_b.id, 251)
