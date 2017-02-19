import aiopg
import asyncio

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


async def prepare_db(models):
    """
    We  create all tables for each of the declared models
    """
    async with aiopg.create_pool(connection) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:

                for model in models:
                    await cur.execute(
                        'DROP TABLE IF EXISTS {table} cascade'.format(
                            table=model().table_name
                        )
                    )
                    await cur.execute(model().creation_query())

                await cur.execute(
                    'DROP TABLE IF EXISTS book_room cascade'.format(
                        table=model().table_name
                    )
                )
                for model in models:
                    m2m_queries = model().get_m2m_field_queries()
                    if m2m_queries:
                        await cur.execute(m2m_queries)


if __name__ == '__main__':
    from test_models.models import Publisher, Book, Author
    task = loop.create_task(prepare_db([Publisher, Author, Book]))
    loop.run_until_complete(asyncio.gather(task))
