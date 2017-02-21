import asyncio
import asyncpg
from datetime import datetime, timedelta
from tests.test_models import Book, Author, Publisher


loop = asyncio.get_event_loop()


class Database_Manager(object):

    def __init__(self):
        self.conn_data = {
            'database': 'sanic',
            'host': 'localhost',
            'user': 'sanicdbuser',
            'password': 'sanicDbPass',
            'loop': loop,
        }
        self.pool = None

    async def get_pool(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(**self.conn_data)
        return self.pool

    async def transaction(self, queries):
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                for query in queries:
                    await conn.execute(query)

    def __del__(self):
        if self.pool:
            self.pool.close()


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
    db = Database_Manager()
    queries = []

    book = Book(**{
        'name': 'silvia',
        'content': 'se va a dormir',
        'date_created': datetime.now() - timedelta(days=23772),
        # 'author': 1
    })

    queries.append(book._db_save())
    await db.transaction(queries)


if __name__ == '__main__':
    task = loop.create_task(create_db([Publisher, Author, Book]))
    loop.run_until_complete(asyncio.gather(task))

    task_queue = []
    for x in range(12):
        task_queue.append(loop.create_task(create_book()))
    loop.run_until_complete(task_queue)
