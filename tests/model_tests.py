from asyncorm.application import get_model
from asyncorm.exceptions import FieldError, ModelError, SerializerError
from asyncorm.serializers import ModelSerializer, SerializerMethod

from .testapp.models import Book, Author
from .testapp.serializer import BookSerializer, BookSerializer2
from .testapp2.models import Developer, Client, Organization
from .test_helper import AioTestCase

# You can get the book by model_name
Book2 = get_model('Book')
# And get the author by module.model_name
Author2 = get_model('testapp.Author')


class ModelTests(AioTestCase):

    def test_class__init__(self):
        # classmethods tests
        # no matter how you import them they are the same object
        self.assertTrue(Author is Author2)
        self.assertTrue(Book is Book2)

        self.assertEqual(Book().cls_tablename(), 'library')
        self.assertEqual(Author().cls_tablename(), 'Author')

    def test_get_fields(self):
        fields = Book.get_fields()

        self.assertEqual(len(fields), 7)
        self.assertEqual(
            sorted(list(fields.keys())),
            sorted(
                ['id', 'content', 'name', 'author', 'date_created', 'price',
                 'quantity']
            )
        )

    def test_get_fields_with_changed_db_column(self):
        fields = Author.get_fields()

        self.assertEqual(len(fields), 5)
        self.assertEqual(
            sorted(list(fields.keys())),
            sorted(['na', 'name', 'age', 'publisher', 'email'])
        )

    def test_instantiated__init__(self):
        # classmethods tests
        book = Book()

        self.assertEqual(book.db_pk, 'id')
        self.assertEqual(book.orm_pk, 'id')

    def test_instantiated__init__with_changed_db_column(self):
        author = Author()

        self.assertEqual(author.db_pk, 'uid')
        self.assertEqual(author.orm_pk, 'na')

    def test_validate_kwargs_wrong_data(self):
        kwargs = {'name': 67}

        # raises the validate content has an incorrect value
        with self.assertRaises(FieldError) as exc:
            book = Book()
            book.validate_kwargs(kwargs)

        self.assertTrue(
            'is a wrong datatype for field' in exc.exception.args[0]
        )

    def test_validate_kwargs_with_forced_id(self):
        kwargs = {'id': 34, 'name': 'name'}

        # also raises fielderror because you can not pre-set the object's id
        with self.assertRaises(FieldError) as exc:
            book = Book()
            book.validate_kwargs(kwargs)

        self.assertEqual(
            exc.exception.args[0],
            'Models can not be generated with forced id'
        )

    def test_validate_kwargs_with_wrong_fieldname(self):
        kwargs = {'name': 'name', 'volume': 23}
        # raises the validate error because volume is not a correct attrib
        with self.assertRaises(ModelError) as exc:
            book = Book()
            book.validate_kwargs(kwargs)

        # its a list because we validate all kwargs
        self.assertEqual(
            exc.exception.args[0],
            ['"volume" is not an attribute for Book', ]
        )

    def test_validate_kwargs_no_error(self):
        kwargs = {'name': 'name'}

        # now it correctly validates
        book = Book()
        book.validate_kwargs(kwargs)

    async def test_ordering(self):
        # since ordering is by id descending
        self.assertEqual(Book().ordering, ['-id'])

        # the first book with id lower that 10
        book = await Book.objects.filter(id__lt=10)[0]

        # is 9
        self.assertEqual(book.id, 9)

    async def test_fk_inverse_relation_exists(self):
        # the inverse relation is correctly set
        self.assertTrue(hasattr(Developer, 'client_set'))

    async def test_fk(self):
        # create a developer
        dev = Developer(name='developboy', age=24)
        await dev.save()

        # a client that has assigned developer
        client = Client(name='devman', dev=dev.id)
        await client.save()
        # get all the developer clients
        clients_returned = dev.client_set()
        client_set = await clients_returned[0]

        # the client has the dev correctly set
        self.assertTrue(client.dev == client.id)
        # and is correct comming back for the other model
        self.assertTrue(client_set.id == dev.id)

    async def test_m2m_inverse_relation_exists(self):
        # the inverse relation is correctly set (not instantiated model)
        self.assertTrue(hasattr(Organization, 'developer_set'))

    async def test_m2m(self):
        # new organization
        org_list = []
        for x in range(1, 6):
            org = Organization(name='ong molona')
            await org.save()
            org_list.append(org.id)

        # create a developer
        dev = Developer(name='developer', age=55, org=org_list)
        await dev.save()
        # and the relation comes back
        # the method exists
        devs_returned = org.developer_set()
        developer_set = await devs_returned[0]
        orgs_returned = dev.organization_set()
        organization_set = await orgs_returned[0]

        # and they are correct
        self.assertEqual(developer_set.id, dev.id)
        self.assertTrue(organization_set.id in org_list)

    async def test_serialize_wrong_argument(self):
        # the inverse relation is correctly set
        q_book = Book.objects.filter(id__lt=100)
        book = await q_book[0]

        # meta fields definition is not correct
        with self.assertRaises(SerializerError) as exc:
            BookSerializer().serialize(book)

        self.assertTrue(
            'is not a correct argument for model' in exc.exception.args[0]
        )

    async def test_serialize_wrong_model(self):
        # complains if we try to serialize an incorrect model
        with self.assertRaises(SerializerError) as exc:
            author = Author()
            BookSerializer2().serialize(author)

        self.assertTrue(
            'That model is not an instance of' in exc.exception.args[0]
        )

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

        self.assertEqual(
            'The serializer has to define the model it\'s serializing',
            exc.exception.args[0]
        )

    async def test_wrong_serializer_no_fields(self):
        # complains if we have a model serializer without model
        with self.assertRaises(SerializerError) as exc:

            class Noone2Serializer(ModelSerializer):

                class Meta:
                    model = Book

        self.assertEqual(
            'The serializer has to define the fields\'s to serialize',
            exc.exception.args[0]
        )

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

        self.assertTrue(
            'its_a_3 is not a correct argument for model' in
            exc.exception.args[0]
        )

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
