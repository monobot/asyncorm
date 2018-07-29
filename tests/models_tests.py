from asyncorm.application.configure import get_model
from asyncorm.exceptions import FieldError, ModelError

from tests.testapp.models import Book, Author
from tests.testapp2.models import Developer, Client, Organization
from tests.test_helper import AioTestCase

# You can get the book by model_name
Book2 = get_model("Book")
# And get the author by module.model_name
Author2 = get_model("testapp.Author")


class ModelTests(AioTestCase):
    def test_class__init__(self):
        # classmethods tests
        # no matter how you import them they are the same object
        self.assertTrue(Author is Author2)
        self.assertTrue(Book is Book2)

        self.assertEqual(Book().cls_tablename(), "library")
        self.assertEqual(Author().cls_tablename(), "Author")

    def test_get_fields(self):
        fields = Book.get_fields()

        self.assertEqual(len(fields), 7)
        self.assertEqual(
            sorted(list(fields.keys())),
            sorted(
                ["id", "content", "name", "author", "date_created", "price", "quantity"]
            ),
        )

    def test_get_fields_with_changed_db_column(self):
        fields = Author.get_fields()

        self.assertEqual(len(fields), 5)
        self.assertEqual(
            sorted(list(fields.keys())),
            sorted(["na", "name", "age", "publisher", "email"]),
        )

    def test_instantiated__init__(self):
        # classmethods tests
        book = Book()

        self.assertEqual(book.db_pk, "id")
        self.assertEqual(book.orm_pk, "id")

    def test_instantiated__init__with_changed_db_column(self):
        author = Author()

        self.assertEqual(author.db_pk, "uid")
        self.assertEqual(author.orm_pk, "na")

    def test_validate_kwargs_wrong_data(self):
        kwargs = {"name": 67}

        # raises the validate content has an incorrect value
        with self.assertRaises(FieldError) as exc:
            book = Book()
            book.validate_kwargs(kwargs)

        self.assertIn("is a wrong datatype for field", exc.exception.args[0])

    def test_validate_kwargs_with_forced_id(self):
        kwargs = {"id": 34, "name": "name"}

        # also raises fielderror because you can not pre-set the object's id
        with self.assertRaises(FieldError) as exc:
            book = Book()
            book.validate_kwargs(kwargs)

        self.assertEqual(
            exc.exception.args[0], "Models can not be generated with forced id"
        )

    def test_validate_kwargs_with_wrong_fieldname(self):
        kwargs = {"name": "name", "volume": 23}
        # raises the validate error because volume is not a correct attrib
        with self.assertRaises(ModelError) as exc:
            book = Book()
            book.validate_kwargs(kwargs)

        # its a list because we validate all kwargs
        self.assertEqual(
            exc.exception.args[0], ['"volume" is not an attribute for Book']
        )

    def test_validate_kwargs_no_error(self):
        kwargs = {"name": "name"}

        # now it correctly validates
        book = Book()
        self.assertEqual(book.validate_kwargs(kwargs), None)

    async def test_ordering(self):
        # since ordering is by id descending
        self.assertEqual(Book().ordering, ["-id"])

        # the first book with id lower that 10
        book = await Book.objects.filter(id__lt=10)[0]

        # is 9
        self.assertEqual(book.id, 9)

    async def test_fk_inverse_relation_exists(self):
        # the inverse relation is correctly set
        self.assertTrue(hasattr(Developer, "client_set"))

    async def test_fk(self):
        # create a developer
        dev = Developer(name="developboy", age=24)
        await dev.save()

        # a client that has assigned developer
        client = Client(name="devman", dev=dev.id)
        await client.save()
        # get all of the developer clients
        clients_returned = dev.client_set()
        client_set = await clients_returned[0]

        # the client has the dev correctly set
        self.assertTrue(client.dev == dev.id)
        # and is correct comming back for the other model
        self.assertTrue(client_set.dev == dev.id)

    async def test_m2m_inverse_relation_exists(self):
        # the inverse relation is correctly set (not instantiated model)
        self.assertTrue(hasattr(Organization, "developer_set"))

    async def test_m2m(self):
        # new organization
        org_list = []
        for _ in range(1, 6):
            org = Organization(name="ong molona")
            await org.save()
            org_list.append(org.id)

        # create a developer
        dev = Developer(name="developer", age=55, org=org_list)
        await dev.save()
        # and the relation comes back
        # the method exists
        devs_returned = org.developer_set()
        developer_set = await devs_returned[0]
        orgs_returned = dev.organization_set()
        organization_set = await orgs_returned[0]

        # and they are correct
        self.assertEqual(developer_set.id, dev.id)
        self.assertIn(organization_set.id, org_list)
