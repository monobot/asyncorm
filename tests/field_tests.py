from asyncorm.exceptions import FieldError
from asyncorm import models
from .testapp.models import Book, Publisher, Reader
from .testapp2.models import Organization
from .test_helper import AioTestCase


class FieldTests(AioTestCase):

    def test_required_kwargs_not_sent(self):

        with self.assertRaises(FieldError) as exc:
            models.CharField()
        self.assertEqual(
            exc.exception.args[0],
            '"CharField" field requires max_length'
        )

    def test_required_kwargs_wrong_value(self):
        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length='gt')

        self.assertEqual(
            exc.exception.args[0],
            'Wrong value for max_length'
        )

    def test_now_correcly_valuates(self):
        # correctly valuates if max_length correctly defined
        models.CharField(max_length=45)

    def test_db_column_validation_wrong_start(self):
        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length=35, db_column='_oneone')

        self.assertEqual(
            exc.exception.args[0],
            'db_column can not start with "_"'
        )

    def test_db_column_validation_wrong_ending(self):
        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length=35, db_column='oneone_')

        self.assertEqual(
            exc.exception.args[0],
            'db_column can not end with "_"'
        )

    def test_db_column_validation_wrong_characters(self):
        with self.assertRaises(FieldError) as exc:
            models.CharField(max_length=35, db_column='one__one')

        self.assertEqual(
            exc.exception.args[0],
            'db_column can not contain "__"'
        )

    def test_db_column_correctly_validates(self):
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

    async def test_choices_display(self):
        book = Book(content='hard cover')

        self.assertEqual(book.content_display(), 'hard cover book')

    async def test_choices_content_not_in_choices(self):
        # choices defined as lists or tuples
        with self.assertRaises(FieldError) as exc:
            book = Book(content='telomero')
            await book.save()

        self.assertEqual(
            exc.exception.args[0],
            '"telomero" not in model choices'
        )

    async def test_dictionary_choices_content_not_in_choices(self):
        # choices defined as dictionaries
        with self.assertRaises(FieldError) as exc:
            read = Reader(power='flower')
            await read.save()

        self.assertEqual(
            exc.exception.args[0],
            '"flower" not in model choices'
        )

    async def test_default_callable(self):
        # when the fields with default value are not esecifically defined
        reader = Reader(size='M')

        await reader.save()

        # they get the default value
        self.assertEqual(reader.name, 'pepito')
        self.assertEqual(reader.weight, 85)

    async def test_jsonfield_saving_dictionary(self):
        publisher = Publisher(name='Oliver', json={'last_name': 'Gregory'})

        await publisher.save()

        self.assertEqual(publisher.json.__class__, dict)

    async def test_jsonfield_saving_wrong_string(self):
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

    async def test_jsonfield_saving_over_max_length(self):
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

    async def test_jsonfield_correct_format(self):
        # only if its correctly formated
        publisher = Publisher(
            name='Oliver',
            json={"last_name": "Gregory", "67": 6}
        )

        await publisher.save()

        self.assertEqual(publisher.json['last_name'], 'Gregory')
        self.assertEqual(publisher.json['67'], 6)

    async def test_booleanfield_validate(self):
        models.BooleanField(default=False).validate(True)

    async def test_booleanfield_validate_wrong_value(self):
        with self.assertRaises(FieldError) as exc:
            models.BooleanField(default=False).validate('laadio@svgvgvcom')

        self.assertEqual(
            'laadio@svgvgvcom is a wrong datatype for field BooleanField',
            exc.exception.args[0]
        )

    async def test_booleanfield_correct(self):
        org = await Organization.objects.create(
            **{'name': 'chapulin', 'active': True, }
        )

        self.assertTrue(org.active)

    def test_emailfield_no_domain_period(self):
        models.EmailField(max_length=35).validate('laadio@s.com')

        with self.assertRaises(FieldError) as exc:
            models.EmailField(max_length=35).validate('laadio@svgvgvcom')

        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])

    def test_emailfield_wrong_starting_char(self):
        with self.assertRaises(FieldError) as exc:
            models.EmailField(max_length=35).validate('@laadio@svgvgv.com')

        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])

    def test_emailfield_wrong_starting_char_2(self):
        with self.assertRaises(FieldError) as exc:
            models.EmailField(
                max_length=35
            ).validate('.laadio@svgv@gv.com')
        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])

    def test_emailfield_wrong_starting_char_3(self):
        with self.assertRaises(FieldError) as exc:
            models.EmailField(
                max_length=35
            ).validate('_laadio@svgv@gv.com')

        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])

    def test_emailfield_too_many_ats(self):
        with self.assertRaises(FieldError) as exc:
            models.EmailField(max_length=35).validate('laadio@svgv@gv.com')

        self.assertTrue(
            'not a valid email address' in exc.exception.args[0])

    def test_emailfield_correct(self):
        models.EmailField(max_length=35).validate('laadio@s.com')
