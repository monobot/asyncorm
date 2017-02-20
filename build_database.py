import aiopg
import asyncio
from datetime import datetime, timedelta
from tests.test_models import Book, Author, Publisher


database_name = 'sanic'
database_host = 'localhost'
database_user = 'sanicdbuser'
database_password = 'sanicDbPass'

connection = 'postgres://{0}:{1}@{2}/{3}'.format(
    database_user,
    database_password,
    database_host,
    database_name
)

loop = asyncio.get_event_loop()


class Database_Manager(object):
    async def transaction(self, queries):
        async with aiopg.create_pool(connection) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute('BEGIN transaction;')
                    for query in queries:
                        await cur.execute(query)
                    await cur.execute('COMMIT transaction;')

    async def non_transaction(self, queries):
        async with aiopg.create_pool(connection) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    async for query in queries:
                        await cur.execute(query)


async def create_db(models):
    """
    We  create all tables for each of the declared models
    """
    db = Database_Manager()
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
    await db.transaction(queries)


async def create_book():
    async with aiopg.create_pool(connection) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:

                book = Book(**{
                    'name': 'silvia',
                    'content': 'se va a dormir',
                    'date_created': datetime.now() - timedelta(days=23772),
                    # 'author': 1
                })

                await cur.execute(book._db_save())


if __name__ == '__main__':
    task = loop.create_task(create_db([Publisher, Author, Book]))
    loop.run_until_complete(asyncio.gather(task))

    # task = loop.create_task(create_book())
    # loop.run_until_complete(asyncio.gather(task))
