import asyncio
import unittest

from .testapp.models import Author, Book

from asyncorm.application import configure_orm

db_config = {
    'database': 'asyncorm',
    'host': 'localhost',
    'user': 'sanicdbuser',
    'password': 'sanicDbPass',
}
orm_app = configure_orm({
    'db_config': db_config,
    'modules': ['tests.testapp', 'tests.testapp2'],
})

loop = orm_app.loop

drop_tables = ['Publisher', 'Author', 'library', 'Organization', 'Developer',
               'Client', 'Developer_Organization', 'Author_Publisher',
               ]


async def clear_table(table_name):
    query = [
        'DROP TABLE IF EXISTS {table_name} CASCADE;'.format(
            table_name=table_name
        ),
    ]
    await orm_app.db_manager.transaction_insert(query)

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


async def test_chainedfilter():
    bk = Book.objects.new_filter(
        id__gte=290,
    ).new_exclude(
        id__lt=295,
    )

    async for b in bk:
        print(b.id)

# create some test models
for x in range(3):
    task = loop.create_task(create_author(x))
    loop.run_until_complete(asyncio.gather(task))
for x in range(300):
    task = loop.create_task(create_book(x))
    loop.run_until_complete(asyncio.gather(task))

task = loop.create_task(test_chainedfilter())
loop.run_until_complete(asyncio.gather(task))


if __name__ == '__main__':
    from .module_tests import ModuleTests
    from .manage_tests import ManageTestMethods
    from .model_tests import ModelTests
    from .field_tests import FieldTests
    from .migration_tests import MigrationTests

    unittest.main()
