import pytest


def pytest_sessionstart(session):
    """ before session.main() is called. """
    print("yes")

def pytest_sessionfinish(session, exitstatus):
    """ whole test run finishes. """
    print("and no")
