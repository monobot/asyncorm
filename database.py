class GeneralManager(object):
    # things that belong to all the diff databases managers
    pass


class PostgresManager(GeneralManager):

    def __init__(self, conn_data):
        self.conn_data = conn_data
        self.conn = None

    async def get_conn(self):
        import asyncpg
        if not self.conn:
            pool = await asyncpg.create_pool(**self.conn_data)
            self.conn = await pool.acquire()
        return self.conn

    async def transaction_insert(self, queries):
        conn = await self.get_conn()
        async with conn.transaction():
            for query in queries:
                result = await conn.execute(query)
        return result

    async def select(self, query):
        conn = await self.get_conn()
        return await conn.fetch(query)

    async def _save(self, queries):
        conn = await self.get_conn()
        async with conn.transaction():
            await conn.execute(queries[0])
            result = await conn.fetch(queries[1])
        return result[0]

    async def _delete(self, query):
        conn = await self.get_conn()
        async with conn.transaction():
            await conn.execute(query)
