from asyncorm.exceptions import *
from asyncorm.fields import *
from .testapp.models import Book, Publisher, Reader
from .test_helper import AioTestCase


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

    async def test_field_max_length(self):
        reader = Reader(size='M', name='name bigger than max')
        with self.assertRaises(FieldError) as exc:
            await reader.save()
        self.assertEqual(
            exc.exception.args[0],
            'The string entered is bigger than the "max_length" defined (15)'
        )

    async def test_choices(self):
        book = Book(content='hard cover')
        self.assertEqual(book.content_display(), 'hard cover book')

        book = Book(content='paperback')
        self.assertEqual(book.content_display(), 'paperback book')

        with self.assertRaises(FieldError) as exc:
            book = Book(content='telomero')
            await book.save()
        self.assertEqual(
            exc.exception.args[0],
            '"telomero" not in model choices'
        )

    async def test_default_callable(self):
        reader = Reader(size='M')
        await reader.save()
        self.assertEqual(reader.name, 'pepito')
        self.assertEqual(reader.weight, 85)

    async def test_jsonfield(self):
        publisher = Publisher(name='Oliver', json={'last_name': 'Gregory'})
        await publisher.save()

        self.assertEqual(publisher.json.__class__, dict)

        # you can also save an string as json
        publisher = Publisher(
            name='Oliver',
            json='{"last_name": "Gregory", 67: 6}'
        )
        with self.assertRaises(FieldError) as exc:
            await publisher.save()
        self.assertEqual(
            exc.exception.args[0],
            'The data entered can not be converted to json'
        )
        # if not bigger than max_length
        publisher = Publisher(
            name='Oliver',
            json='{"last_name": "Gregory", "67": 6, "totorota": "of course"}'
        )
        with self.assertRaises(FieldError) as exc:
            await publisher.save()
        self.assertEqual(
            exc.exception.args[0],
            'The string entered is bigger than the "max_length" defined (50)'
        )
        # only if its correctly formated
        publisher = Publisher(
            name='Oliver',
            json={"last_name": "Gregory", "67": 6}
        )
        await publisher.save()
        self.assertEqual(publisher.json['last_name'], 'Gregory')
        self.assertEqual(publisher.json['67'], 6)
