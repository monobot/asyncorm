import unittest
import asyncio
from datetime import datetime, timedelta

from exceptions import *
from tests.test_models import Book, Author
from fields import *


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

        self.assertEqual(book._fk_db_fieldname, 'id')
        self.assertEqual(book._fk_orm_fieldname, 'id')

        author = Author()

        self.assertEqual(author._fk_db_fieldname, 'uid')
        self.assertEqual(author._fk_orm_fieldname, 'na')

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

    # def test__db_save(self):
    #     from datetime import datetime

    #     book = Book(**{
    #         'name': 'name asigned',
    #         'content': 'content asigned',
    #         'date_created': datetime.now(),
    #         # 'author': 1
    #     })
    #     book._db_save()


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
        book = Book(content='tapa dura')
        self.assertEqual(book.content_display(), 'libro de tapa dura')

        book = Book(content='tapa blanda')
        self.assertEqual(book.content_display(), 'libro de tapa blanda')


class ManageTestMethods(AioTestCase):

    async def test_save(self):
        book = Book(**{
            'name': 'silvia',
            'content': 'tapa dura',
            'date_created': datetime.now() - timedelta(days=23772),
            # 'author': 1
        })
        self.assertFalse(book.id)

        await book.save()
        self.assertTrue(book.id)

        orig_id = book.id

        await book.save()
        self.assertEqual(orig_id, book.id)

    async def test_filter(self):
        queryset = await Book.objects.filter(id__gt=280, name='silvia')

        self.assertTrue(len(queryset) >= 20)
        self.assertTrue(isinstance(queryset[0], Book))

        # empty queryset
        queryset = await Book.objects.filter(id__gt=2800, name='silvia')
        self.assertEqual(len(queryset), 0)

    async def test_get(self):
        book = await Book.objects.get(id=280, name='silvia')

        self.assertTrue(isinstance(book, Book))

        # now try to get using wrong arguments
        with self.assertRaises(QuerysetError) as exc:
            await Book.objects.get(id__gt=280, name='silvia')
        self.assertTrue(
            'More than one Book where returned, there are' in
            exc.exception.args[0]
        )


if __name__ == '__main__':
    unittest.main()
