class Cursor(object):
    """Generates a Database Cursor to be used by the ORM."""

    def __init__(self, conn, query, values=None, step=20, forward=0, stop=None):
        self._conn = conn
        self._query = query
        self._values = values
        self._cursor = None
        self._results = []

        self._step = step
        self._forward = forward
        self._stop = stop
        self._iddle = True

    async def get_results(self):
        self._iddle = False
        async with self._conn.transaction():
            if self._values:
                self._cursor = await self._conn.cursor(self._query, self._values)
            else:
                self._cursor = await self._conn.cursor(self._query)

            if self._forward:
                await self._cursor.forward(self._forward)

            no_stop = self._stop is not None
            if no_stop and self._forward >= self._stop:
                raise StopAsyncIteration()
            if no_stop and self._forward + self._step >= self._stop:
                self._step = self._stop - self._forward

            results = await self._cursor.fetch(self._step)

            if not results:
                raise StopAsyncIteration()
        self._iddle = True
        return results

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._cursor is None:
            self._results = await self.get_results()

        if not self._results:
            self._forward = self._forward + self._step
            if self._stop is not None and self._forward > self._stop:
                self._forward = self._stop
            self._results = await self.get_results()

        return self._results.pop(0)
