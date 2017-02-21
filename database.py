import asyncpg


class Database_Manager(object):

    def __init__(self):
        self.conn_data = {
            'database': 'sanic',
            'host': 'localhost',
            'user': 'sanicdbuser',
            'password': 'sanicDbPass',
            # 'loop': loop,
        }
        self.conn = None

    async def get_conn(self):
        if not self.conn:
            pool = await asyncpg.create_pool(**self.conn_data)
            self.conn = await pool.acquire()
        return self.conn

    async def transaction_insert(self, queries):
        conn = await self.get_conn()
        async with conn.transaction():
            for query in queries:
                await conn.execute(query)

    async def select(self, query):
        conn = await self.get_conn()
        return await conn.fetch(query)
