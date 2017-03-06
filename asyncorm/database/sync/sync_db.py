import asyncio

from ...application import orm_app

dm = orm_app.db_manager
loop = orm_app.loop


async def create_db():
    """
    We  create all tables for each of the declared models
    """
    queries = []
    delayed = []

    queries.append('DROP TABLE IF EXISTS Author_Publisher CASCADE')
    queries.append('DROP TABLE IF EXISTS Developer_Organization CASCADE')

    for model in orm_app.models.values():
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


def sync_db():
    task = loop.create_task(create_db())
    loop.run_until_complete(asyncio.gather(task))
