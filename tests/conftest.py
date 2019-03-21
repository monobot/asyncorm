import asyncio
import os

import pytest

from asyncorm.application import configure_orm


@pytest.yield_fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def orm_setup(request, event_loop):
    config_file = os.path.join(os.getcwd(), "tests", "asyncorm.ini")
    orm = configure_orm(config_file, loop=event_loop)

    event_loop.run_until_complete(orm.db_backend.transaction_start())
    yield orm
    event_loop.run_until_complete(orm.db_backend.transaction_start())
