import asyncio
from datetime import datetime, timedelta
from tests.test_models import Book, Author, Publisher
from database import Database_Manager

loop = asyncio.get_event_loop()

db = Database_Manager()


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
        queries.append(model()._creation_query())

    queries.append(
        'DROP TABLE IF EXISTS author_publisher cascade'.format(
            table=model().table_name
        )
    )
    for model in models:
        m2m_queries = model()._get_m2m_field_queries()
        if m2m_queries:
            queries.append(m2m_queries)
    await db.transaction_insert(queries)


async def create_book():
    queries = []

    book = Book(**{
        'name': 'silvia',
        'content': 'se va a dormir',
        'date_created': datetime.now() - timedelta(days=23772),
        # 'author': 1
    })

    queries.append(book._db_save())
    await db.transaction_insert(queries)


async def fetch_book():
    return await db.select(Book.objects._get_objects_query())


if __name__ == '__main__':
    task = loop.create_task(create_db([Publisher, Author, Book]))
    loop.run_until_complete(asyncio.gather(task))

    task_queue = []
    for x in range(70):
        task_queue.append(loop.create_task(create_book()))
    loop.run_until_complete(asyncio.gather(*task_queue))

    task = loop.create_task(fetch_book())
    loop.run_until_complete(asyncio.gather(task))
