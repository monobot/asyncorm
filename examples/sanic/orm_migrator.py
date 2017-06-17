import asyncio

from asyncorm.application.commands.migrator import migrator

loop = asyncio.get_event_loop()

task = loop.create_task(migrator())
loop.run_until_complete(asyncio.gather(task))
