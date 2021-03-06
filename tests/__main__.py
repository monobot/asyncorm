import asyncio
import os
import unittest

from asyncorm.application import configure_orm
from tests.app_1.models import Author, Book

config_file = os.path.join(os.getcwd(), "tests", "asyncorm.ini")
orm_app = configure_orm(config_file)

loop = orm_app.loop

drop_tables = [
    "Publisher",
    "Author",
    "library",
    "Organization",
    "Developer",
    "Client",
    "Developer_Organization",
    "Author_Publisher",
    "Appointment",
    "Reader",
    "Skill",
]


async def clear_table(table_name):
    query = orm_app.db_backend._construct_query([{"action": "_db__drop_table", "table_name": table_name}])
    await orm_app.db_backend.request(query)


for table_name in drop_tables:
    task = loop.create_task(clear_table(table_name))
    loop.run_until_complete(asyncio.gather(task))

orm_app.sync_db()


async def create_book(x):
    book = Book(name="book name {}".format(str(x)), content="hard cover")

    await book.save()


async def create_author(x):
    author = Author(name="foo_boy {}".format(str(x)), age=23)

    await author.save()


# create some test models
for x in range(3):
    task = loop.create_task(create_author(x))
    loop.run_until_complete(asyncio.gather(task))

for x in range(300):
    task = loop.create_task(create_book(x))
    loop.run_until_complete(asyncio.gather(task))


if __name__ == "__main__":
    from tests.test_fields import FieldTests
    from tests.test_manage import ManageTestMethods
    from tests.test_migration import MigrationTests
    from tests.test_models import ModelTests
    from tests.test_module import ModuleTests
    from tests.test_serializers import SerializerTests

    unittest.main()
