import asyncio
import os
import pytest

from tests.app_1.models import Author, Book


def pytest_sessionstart(session):
    """ before session.main() is called. """
    print("yes")


def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """
    print("and no")
