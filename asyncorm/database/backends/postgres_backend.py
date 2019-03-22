import asyncpg

from asyncorm.database.backends.sql_base_backend import SQLBaseBackend
from asyncorm.database.cursor import Cursor
from asyncorm.database.query_stack import QueryStack


class PostgresBackend(SQLBaseBackend):
    """PostgresBackend serves as interface with the postgres database."""

    def __init__(self, conn_data: dict) -> None:
        self.test = conn_data.get("test", False)
        self._connection_data = conn_data
        self._connection = None
        self._pool = None

    async def _get_pool(self) -> asyncpg.pool.Pool:
        """Get a connections pool from the database.

        :return: connection pool
        :rtype: asyncpg pool
        """
        if not self._pool:
            self._pool = await asyncpg.create_pool(**self._connection_data)
        return self._pool

    def get_sync_connection(self, loop: "asyncio.loop") -> asyncpg.connection.Connection:
        """Get the connection synchronously.

        :param loop: loop that will manage the coroutine.
        :type asyncio.loop:
        :return: the postgres connection
        :rtype: asyncpg.connection.Connection
        """
        loop.run_until_complete(self._get_connection())
        return self._connection

    async def _get_connection(self) -> asyncpg.connection.Connection:
        """Set a connection to the database.

        :return: Connection set
        :rtype: asyncpg.connection
        """
        if self._connection is None:
            self._pool = await self._get_pool()
            self._connection = await self._pool.acquire()

        return self._connection

    async def get_cursor(self, query: dict, forward: int, stop: int) -> Cursor:
        """Get a new cursor.

        :param query: Query to be constructed.
        :type query: dict
        :param forward: Next step in the cursor.
        :type forward: int
        :param stop: Last step in the cursorself.
        :type stop: int
        :return: New Cursor
        :rtype: Cursor
        """
        await self._get_connection()
        query = self._construct_query(query)
        return Cursor(self._connection, query[0], values=query[1], forward=forward, stop=stop)

    async def transaction_start(self):
        """Start the transaction."""
        self._connection = await self._get_connection()

        self.transaction = self._connection.transaction()
        await self.transaction.start()

    async def transaction_commit(self):
        """Commit the transaction."""
        await self.transaction.commit()

    async def transaction_rollback(self):
        """Rollback the transaction."""
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
