import unittest

from .module_tests import *
from .manage_tests import *
from .model_tests import *
from .field_tests import *

from asyncorm.application import configure_orm

db_config = {
    'database': 'asyncorm',
    'host': 'localhost',
    'user': 'sanicdbuser',
    'password': 'sanicDbPass',
}
configure_orm({
    'db_config': db_config,
    'modules': ['tests.testapp', 'tests.testapp2'],
})

dm = orm_app.db_manager
loop = orm_app.loop


async def create_db(models):
    """
    We  create all tables for each of the declared models
    """
    queries = []
    delayed = []

    queries.append('DROP TABLE IF EXISTS Author_Publisher CASCADE')
    queries.append('DROP TABLE IF EXISTS Developer_Organization CASCADE')

    for model in models:
        queries.append(
            'DROP TABLE IF EXISTS {table} CASCADE'.format(
                table=model().table_name
            )
        )
        queries.append(model.objects._creation_query())

        m2m_queries = model.objects._get_m2m_field_queries()
        if m2m_queries:
            delayed.append(m2m_queries)

    result = await dm.transaction_insert(queries + delayed)
    return result


async def create_book(x):
    book = Book(**{
        'name': 'book name {}'.format(str(x)),
        'content': 'hard cover',
    })

    await book.save()


async def create_author(x):
    book = Author(**{
        'name': 'pedrito {}'.format(str(x)),
        'age': 23,
    })

    await book.save()

task = loop.create_task(create_db(orm_app.models.values()))
loop.run_until_complete(asyncio.gather(task))

# create some test models
for x in range(3):
    task = loop.create_task(create_author(x))
    loop.run_until_complete(asyncio.gather(task))
for x in range(300):
    task = loop.create_task(create_book(x))
    loop.run_until_complete(asyncio.gather(task))
if __name__ == '__main__':
    unittest.main()
