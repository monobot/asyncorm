import asyncio
import unittest
import os

from .testapp.models import Author, Book

from asyncorm.application import configure_orm

config_file = os.path.join(os.getcwd(), 'tests', 'asyncorm.ini')
orm_app = configure_orm(config_file)

loop = orm_app.loop

drop_tables = [
    'Publisher', 'Author', 'library', 'Organization', 'Developer', 'Client',
    'Developer_Organization', 'Author_Publisher', 'Appointment', 'Reader'
]


async def clear_table(table_name):
    query = orm_app.db_manager.construct_query(
        [{'action': 'db__drop_table', 'table_name': table_name}]
    )
    await orm_app.db_manager.request(query)

for table_name in drop_tables:
    task = loop.create_task(clear_table(table_name))
    loop.run_until_complete(asyncio.gather(task))

orm_app.sync_db()


async def create_book(x):
    book = Book(**{
        'name': 'book name {}'.format(str(x)),
        'content': 'hard cover',
    })

    await book.save()


async def create_author(x):
    author = Author(**{
        'name': 'foo_boy {}'.format(str(x)),
        'age': 23,
    })

    await author.save()

# create some test models
for x in range(3):
    task = loop.create_task(create_author(x))
    loop.run_until_complete(asyncio.gather(task))
for x in range(300):
    task = loop.create_task(create_book(x))
    loop.run_until_complete(asyncio.gather(task))


if __name__ == '__main__':
    from .model_tests import ModelTests
    from .manage_tests import ManageTestMethods
    from .module_tests import ModuleTests
    from .field_tests import FieldTests
    from .migration_tests import MigrationTests

    unittest.main()
