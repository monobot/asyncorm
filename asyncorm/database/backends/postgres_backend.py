import asyncpg

from asyncorm.database.backends.sql_base_backend import SQLBaseBackend
from asyncorm.database.cursor import Cursor
from asyncorm.database.query_list import QueryStack


class PostgresBackend(SQLBaseBackend):
    def __init__(self, conn_data):
        self.test = conn_data.get("test", False)
        self._connection_data = conn_data
        self._connection = None
        self._pool = None

    async def _check_transaction(self, transaction):
        if self.test:
            await transaction.rollback()
        else:
            await transaction.commit()

    async def _get_pool(self):
        """Get a connections pool from the database.

        :return: connection pool
        :rtype: asyncpg pool
        """
        if not self._pool:
            self._pool = await asyncpg.create_pool(**self._connection_data)
        return self._pool

    def get_sync_connection(self, loop):
        loop.run_until_complete(self._get_connection())
        return self._connection

    async def _get_connection(self):
        """Set a connection to the database.

        :return: Connection set
        :rtype: asyncpg.connection
        """
        if self._connection is None:
            self._pool = await self._get_pool()
            self._connection = await self._pool.acquire()

        return self._connection

    async def get_cursor(self, query, forward, stop):
        await self._get_connection()
        query = self._construct_query(query)
        return Cursor(self._connection, query[0], values=query[1], forward=forward, stop=stop)

    async def transaction_start(self):
        self._connection = await self._get_connection()

        self.transaction = self._connection.transaction()
        await self.transaction.start()

    async def transaction_commit(self):
        await self.transaction.commit()

    async def transaction_rollback(self):
        await self.transaction.rollback()

    async def request(self, query):
        """Send a database request inside a transaction.

        :param query: sql sentence
        :type query: str
        :return: asyncpg Record object
        :rtype: asyncpg.Record
        """
        QueryStack.append(query)

        conn = await self._get_connection()

        if isinstance(query, (tuple, list)):
            if query[1]:
                query_result = await conn.fetchrow(query[0], *query[1])
                return query_result

            else:
                query_result = await conn.fetchrow(query[0])
                return query_result

        query_result = await conn.fetchrow(query)

        return query_result
