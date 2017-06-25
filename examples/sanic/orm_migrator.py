import asyncio

from asyncorm.application.commands.migrator import Migrator

loop = asyncio.get_event_loop()

migrator = Migrator()
task = loop.create_task(migrator.run())
loop.run_until_complete(asyncio.gather(task))
