import asyncio

from logic import get_data, process_data


class GenericQueueAsyncIter:

    def __init__(self, queue: asyncio.Queue):
        self._queue = queue
        self._stoped = False

    async def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._stoped:
            data = await self._queue.get()
            if isinstance(data, StopIteration):
                self._stoped = True
                raise StopAsyncIteration()
            else:
                return data

        raise StopAsyncIteration()


async def data_producer_task(queue):
    "this is a asyncio task, is like a thread"

    while True:
        data = await get_data()
        await queue.put(data)


async def data_consumer_task(queue):
    aiter = GenericQueueAsyncIter(queue)
    async for data in aiter:
        await process_data(data)


queue = asyncio.Queue(1000)
producer_task = asyncio.ensure_future(data_producer_task(queue))
consumer_task = asyncio.ensure_future(data_consumer_task(queue))

loop = asyncio.get_event_loop()

loop.run_until_complete([producer_task, consumer_task])
