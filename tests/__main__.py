import asyncio
import unittest

from datetime import datetime, timedelta

# from application import OrmApp
from asyncorm.application import configure_orm
from asyncorm.exceptions import *
from asyncorm.fields import *
from asyncorm.model import Model


BOOK_CHOICES = (
    ('hard cover', 'hard cover book'),
    ('paperback', 'paperback book')
)

dm = None
if not dm:
    orm = configure_orm({'db_config': {
            'database': 'asyncorm',
            'host': 'localhost',
            'user': 'sanicdbuser',
            'password': 'sanicDbPass',
        }})
    dm = orm.db_manager
    loop = asyncio.get_event_loop()


class Publisher(Model):
    name = CharField(max_length=50)


class Book(Model):
    table_name = 'library'
    name = CharField(max_length=50)
    content = CharField(max_length=255, choices=BOOK_CHOICES)
    date_created = DateField(auto_now=True)
    author = ForeignKey(foreign_key='Author', null=True)

    class Meta():
        ordering = ['-id']
        unique_together = ['name', 'content']


class Author(Model):
    na = PkField(field_name='uid')
    name = CharField(max_length=50, unique=True)
    age = IntegerField()
    publisher = ManyToMany(foreign_key='Publisher')


async def create_db(models):
    """
    We  create all tables for each of the declared models
    """
    queries = []

    for model in models:
        queries.append(
            'DROP TABLE IF EXISTS {table} cascade'.format(
                table=model().table_name
            )
        )
        queries.append(model().objects._creation_query())

    queries.append(
        'DROP TABLE IF EXISTS author_publisher cascade'.format(
            table=model().table_name
        )
    )
    for model in models:
        m2m_queries = model().objects._get_m2m_field_queries()
        if m2m_queries:
            queries.append(m2m_queries)
    result = await dm.transaction_insert(queries)
    return result


async def create_book(x):
    book = Book(**{
        'name': 'book name {}'.format(str(x)),
        'content': 'hard cover',
        # 'date_created': datetime.now() - timedelta(days=23772),
    })

    await book.save()


async def create_author(x):
    book = Author(**{
        'name': 'pedrito {}'.format(str(x)),
        'age': 23,
    })

    await book.save()

# clear and recreate the database
task = loop.create_task(create_db([Author, Publisher, Book]))
loop.run_until_complete(asyncio.gather(task))

# create some test models
for x in range(3):
    task = loop.create_task(create_author(x))
    loop.run_until_complete(asyncio.gather(task))
for x in range(300):
    task = loop.create_task(create_book(x))
    loop.run_until_complete(asyncio.gather(task))


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
        pass


class ModelTests(AioTestCase):

    def test_class__init__(self):
        # classmethods tests
        self.assertEqual(Book().table_name, 'library')
        self.assertEqual(Author().table_name, 'author')

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


class FieldTests(AioTestCase):

    def test_required_kwargs(self):

        with self.assertRaises(FieldError) as exc:
            CharField()
        self.assertEqual(
            exc.exception.args[0],
            '"CharField" field requires max_length'
        )

        with self.assertRaises(FieldError) as exc:
            CharField(max_length='gt')
        self.assertEqual(
            exc.exception.args[0],
            'Wrong value for max_length'
        )
        # correctly valuates if max_length correctly defined
        CharField(max_length=45)

        with self.assertRaises(FieldError) as exc:
            ForeignKey()
        self.assertEqual(
            exc.exception.args[0],
            '"ForeignKey" field requires foreign_key'
        )
        with self.assertRaises(FieldError) as exc:
            ForeignKey(foreign_key=56)
        self.assertEqual(
            exc.exception.args[0],
            'Wrong value for foreign_key'
        )
        # correctly valuates if foreign_key correctly defined
        ForeignKey(foreign_key='366')

        with self.assertRaises(FieldError) as exc:
            ManyToMany()
        self.assertEqual(
            exc.exception.args[0],
            '"ManyToMany" field requires foreign_key'
        )
        with self.assertRaises(FieldError) as exc:
            ManyToMany(foreign_key=56)
        self.assertEqual(
            exc.exception.args[0],
            'Wrong value for foreign_key'
        )
        # correctly valuates if foreign_key correctly defined
        ManyToMany(foreign_key='366')

    def test_field_name(self):
        with self.assertRaises(FieldError) as exc:
            CharField(max_length=35, field_name='_oneone')
        self.assertEqual(
            exc.exception.args[0],
            'field_name can not start with "_"'
        )

        with self.assertRaises(FieldError) as exc:
            CharField(max_length=35, field_name='oneone_')
        self.assertEqual(
            exc.exception.args[0],
            'field_name can not end with "_"'
        )

        with self.assertRaises(FieldError) as exc:
            CharField(max_length=35, field_name='one__one')
        self.assertEqual(
            exc.exception.args[0],
            'field_name can not contain "__"'
        )

        # this is an allowed fieldname
        CharField(max_length=35, field_name='one_one')

    def test_choices(self):
        book = Book(content='hard cover')
        self.assertEqual(book.content_display(), 'hard cover book')

        book = Book(content='paperback')
        self.assertEqual(book.content_display(), 'paperback book')


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
        book = Book(**{
            'name': 'book name 5',
            'content': 'hard cover',
        })
        with self.assertRaises(ModelError) as exc:
            await book.save()
        self.assertTrue(
            'The model violates a unique constraint' == exc.exception.args[0]
        )

        # but when any of them are different there is no problem
        book.name = 'this is a new name'
        await book.save()

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
            'only allows tuples of size 2') in
            exc.exception.args[0]
        )

        # incorrect fitler tuple definition error catched
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id=(280, ))
        self.assertTrue(
            ('Not a correct tuple definition, filter '
            'only allows tuples of size 2') in
            exc.exception.args[0]
        )

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
