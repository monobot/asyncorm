import asyncpg

from asyncorm.database.cursor import Cursor
from asyncorm.database.query_list import QueryStack
from asyncorm.exceptions import AsyncormTransactionRollback
from asyncorm.log import logger

from asyncorm.database.backends.sql_base_backend import SQLBaseBackend


class PostgresBackend(SQLBaseBackend):
    def __init__(self, conn_data):
        self._conn_data = conn_data
        self._conn = None
        self._pool = None

    async def _get_pool(self):
        """Get a connections pool from the database.

        :return: connection pool
        :rtype: asyncpg pool
        """
        if self._pool is None:
            self._pool = await asyncpg.create_pool(**self._conn_data)
        return self._pool

    async def _get_connection(self):
        """Set a connection to the database.

        :return: Connection set
        :rtype: asyncpg.connection
        """
        if not self._conn:
            self._pool = await self._get_pool()
            self._conn = await self._pool.acquire()

        return self._conn

    async def get_cursor(self, query, forward, stop):
        await self._get_connection()
        query = self._construct_query(query)
        return Cursor(self._conn, query[0], values=query[1], forward=forward, stop=stop)

    async def transaction_init(self):
        pass

    async def transaction_rollback(self):
        pass

    async def request(self, query):
        """Send a database request inside a transaction.

        :param query: sql sentence
        :type query: str
        :return: asyncpg Record object
        :rtype: asyncpg.Record
        """
        QueryStack.append(query)
        await self._get_pool()

        conn = await self._get_connection()
        async with conn.transaction():
            if isinstance(query, (tuple, list)):
                if query[1]:
                    return await conn.fetchrow(query[0], *query[1])
                else:
                    return await conn.fetchrow(query[0])
            return await conn.fetchrow(query)

        self._conn = await self._pool.acquire()
