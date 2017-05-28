from asyncorm.exceptions import FieldError
from asyncorm import models
from .testapp.models import Book, Publisher, Reader
from .testapp2.models import Organization
from .test_helper import AioTestCase


class FieldTests(AioTestCase):

    def test_required_kwargs(self):

        with self.assertRaises(FieldError) as exc:
            models.CharField()
        self.assertEqual(
            exc.exception.args[0],
            '"CharField" field requires max_length'
        )

        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length='gt')
        self.assertEqual(
            exc.exception.args[0],
            'Wrong value for max_length'
        )
        # correctly valuates if max_length correctly defined
        models.CharField(max_length=45)

        with self.assertRaises(FieldError) as exc:
            models.ForeignKey()
        self.assertEqual(
            exc.exception.args[0],
            '"ForeignKey" field requires foreign_key'
        )
        with self.assertRaises(FieldError) as exc:
            models.ForeignKey(foreign_key=56)
        self.assertEqual(
            exc.exception.args[0],
            'Wrong value for foreign_key'
        )
        # correctly valuates if foreign_key correctly defined
        models.ForeignKey(foreign_key='366')

        with self.assertRaises(FieldError) as exc:
            models.ManyToManyField()
        self.assertEqual(
            exc.exception.args[0],
            '"ManyToManyField" field requires foreign_key'
        )
        with self.assertRaises(FieldError) as exc:
            models.ManyToManyField(foreign_key=56)
        self.assertEqual(
            exc.exception.args[0],
            'Wrong value for foreign_key'
        )
        # correctly valuates if foreign_key correctly defined
        models.ManyToManyField(foreign_key='366')

    def test_field_name(self):
        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length=35, db_column='_oneone')
        self.assertEqual(
            exc.exception.args[0],
            'db_column can not start with "_"'
        )

        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length=35, db_column='oneone_')
        self.assertEqual(
            exc.exception.args[0],
            'db_column can not end with "_"'
        )

        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length=35, db_column='one__one')
        self.assertEqual(
            exc.exception.args[0],
            'db_column can not contain "__"'
        )

        # this is an allowed fieldname
        models.CharField(max_length=35, db_column='one_one')

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

        # choices defined as lists or tuples
        with self.assertRaises(FieldError) as exc:
            book = Book(content='telomero')
            await book.save()
        self.assertEqual(
            exc.exception.args[0],
            '"telomero" not in model choices'
        )
        # choices defined as dictionaries
        with self.assertRaises(FieldError) as exc:
            read = Reader(power='flower')
            await read.save()
        self.assertEqual(
            exc.exception.args[0],
            '"flower" not in model choices'
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

    async def test_booleanfield(self):
        models.BooleanField(default=False).validate(True)

        with self.assertRaises(FieldError) as exc:
            models.BooleanField(default=False).validate('laadio@svgvgvcom')
        self.assertEqual(
            'laadio@svgvgvcom is a wrong datatype for field BooleanField',
            exc.exception.args[0]
        )

        org = await Organization.objects.create(
            **{'name': 'chapulin', 'active': True, }
        )
        self.assertTrue(org.active)

    def test_emailfield(self):
        models.EmailField(max_length=35).validate('laadio@s.com')

        with self.assertRaises(FieldError) as exc:
            models.EmailField(
                max_length=35
            ).validate('laadio@svgvgvcom')
        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])
        with self.assertRaises(FieldError) as exc:
            models.EmailField(
                max_length=35
            ).validate('@laadio@svgvgv.com')
        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])
        with self.assertRaises(FieldError) as exc:
            models.EmailField(
                max_length=35
            ).validate('laadio@svgv@gv.com')
        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])
        with self.assertRaises(FieldError) as exc:
            models.EmailField(
                max_length=35
            ).validate('.laadio@svgv@gv.com')
        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])
        with self.assertRaises(FieldError) as exc:
            models.EmailField(
                max_length=35
            ).validate('_laadio@svgv@gv.com')
        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])
