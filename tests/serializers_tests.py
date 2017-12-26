from asyncorm.application import get_model
from asyncorm.exceptions import SerializerError
from asyncorm.serializers import ModelSerializer, SerializerMethod

from .testapp.models import Book, Author
from .testapp.serializer import BookSerializer, BookSerializer2
from .test_helper import AioTestCase

# You can get the book by model_name
Book2 = get_model('Book')
# And get the author by module.model_name
Author2 = get_model('testapp.Author')


class SerializerTests(AioTestCase):

    async def test_serialize_wrong_argument(self):
        # the inverse relation is correctly set
        q_book = Book.objects.filter(id__lt=100)
        book = await q_book[0]

        # meta fields definition is not correct
        with self.assertRaises(SerializerError) as exc:
            BookSerializer().serialize(book)

        self.assertIn('is not a correct argument for model', exc.exception.args[0])

    async def test_serialize_wrong_model(self):
        # complains if we try to serialize an incorrect model
        with self.assertRaises(SerializerError) as exc:
            author = Author()
            BookSerializer2().serialize(author)

        self.assertIn('That model is not an instance of', exc.exception.args[0])

    async def test_serialize_correct(self):
        # the inverse relation is correctly set
        q_book = Book.objects.filter(id__lt=100)
        book = await q_book[0]

        serialized_book = BookSerializer2().serialize(book)

        self.assertEqual(serialized_book.get('name'), 'book name 98')

    async def test_wrong_serializer_no_model(self):
        # complains if we have a model serializer without model
        with self.assertRaises(SerializerError) as exc:

            class NooneSerializer(ModelSerializer):

                class Meta:
                    fields = ['name', 'content', ]

        self.assertEqual('The serializer has to define the model it\'s serializing', exc.exception.args[0])

    async def test_wrong_serializer_no_fields(self):
        # complains if we have a model serializer without model
        with self.assertRaises(SerializerError) as exc:

            class Noone2Serializer(ModelSerializer):

                class Meta:
                    model = Book

        self.assertEqual('The serializer has to define the fields\'s to serialize', exc.exception.args[0])

    async def test_wrong_serializer_not_defined_methodfield(self):
        # complains if we have a model serializer without model
        with self.assertRaises(SerializerError) as exc:
            class BookSerializerNew(ModelSerializer):
                its_a_2 = SerializerMethod()

                def get_its_a_2(self, instance):
                    return instance.its_a_2()

                class Meta:
                    model = Book
                    fields = ['its_a_2', 'its_a_3', ]

            BookSerializerNew().serialize(await Book.objects.get(id=3))

        self.assertIn('its_a_3 is not a correct argument for model', exc.exception.args[0])

    async def test_serializer_correctly_defined_methodfield(self):
        class BookSerializerNew(ModelSerializer):
            its_a_2 = SerializerMethod()

            def get_its_a_2(self, instance):
                return instance.its_a_2()

            class Meta:
                model = Book
                fields = ['its_a_2', ]

        book_ser = BookSerializerNew().serialize(await Book.objects.get(id=3))
        self.assertEqual(book_ser['its_a_2'], 2)
