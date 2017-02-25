import asyncio
from datetime import datetime, timedelta
from tests.test_models import Book, Author, Publisher
from database import PostgresManager

loop = asyncio.get_event_loop()

dm = PostgresManager({
    'database': 'asyncorm',
    'host': 'localhost',
    'user': 'sanicdbuser',
    'password': 'sanicDbPass',
    # 'loop': loop,
})


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
    result = await dm.transaction_insert(queries)
    return result


async def create_book():
    book = Book(**{
        'name': 'silvia',
        'content': 'tapa dura',
        'date_created': datetime.now() - timedelta(days=23772),
        # 'author': 1
    })

    await book.save()


async def fetch_books():
    return await Book.objects.filter(id__gt=280, name='silvia')


async def get_book():
    return await Book.objects.get(id=280, name='silvia')


if __name__ == '__main__':
    task = loop.create_task(create_db([Author, Publisher, Book]))
    loop.run_until_complete(asyncio.gather(task))

    for x in range(300):
        task = loop.create_task(create_book())
        loop.run_until_complete(asyncio.gather(task))
