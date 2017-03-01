import asyncio

from datetime import datetime, timedelta

from asyncorm.tests import Book, Author, Publisher
from asyncorm.application import configure_orm, orm_app

dm = orm_app.db_manager
loop = orm_app.loop

if not dm:
    orm = configure_orm({'db_config': {
            'database': 'asyncorm',
            'host': 'localhost',
            'user': 'sanicdbuser',
            'password': 'sanicDbPass',
        }})
    dm = orm.db_manager
    loop = asyncio.get_event_loop()


async def create_db(models):
    """
    We  create all tables for each of the declared models
    """
    queries = []

    for model in models:
        queries.append(
            'DROP TABLE IF EXISTS {table} cascade'.format(
                table=model().table_name
            )
        )
        queries.append(model().objects._creation_query())

    queries.append(
        'DROP TABLE IF EXISTS author_publisher cascade'.format(
            table=model().table_name
        )
    )
    for model in models:
        m2m_queries = model().objects._get_m2m_field_queries()
        if m2m_queries:
            queries.append(m2m_queries)
    result = await dm.transaction_insert(queries)
    return result


async def create_book():
    book = Book(**{
        'name': 'book name',
        'content': 'hard cover',
        'date_created': datetime.now() - timedelta(days=23772),
        # 'author': 1
    })

    await book.save()


async def create_author():
    book = Author(**{
        'name': 'pedrito',
        'age': 23,
    })

    await book.save()


if __name__ == '__main__':
    task = loop.create_task(create_db([Author, Publisher, Book]))
    loop.run_until_complete(asyncio.gather(task))

    for x in range(300):
        task = loop.create_task(create_book())
        loop.run_until_complete(asyncio.gather(task))
