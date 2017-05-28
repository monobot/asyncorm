===============================
asyncOrm
===============================

.. image:: https://img.shields.io/pypi/v/asyncorm.svg
    :target: https://pypi.python.org/pypi/asyncorm
    :alt: Pypi package
.. image:: https://img.shields.io/pypi/pyversions/asyncorm.svg
    :target: https://pypi.python.org/pypi/asyncorm
    :alt: Python versions
.. image:: https://api.codacy.com/project/badge/Grade/86ee891909654fc0a294849d0a436109
    :target: https://www.codacy.com/app/monobot/asyncorm?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=monobot/asyncorm&amp;utm_campaign=Badge_Grade
    :alt: Code quality

.. image:: https://pyup.io/repos/github/monobot/asyncorm/shield.svg
    :target: https://pyup.io/account/repos/github/monobot/asyncorm/
    :alt: Packages status
.. image:: https://codecov.io/github/monobot/asyncorm/development.svg
    :target: https://codecov.io/github/monobot/asyncorm/
    :alt: Code coverage
.. image:: https://travis-ci.org/monobot/asyncorm.svg?branch=development
    :target: https://travis-ci.org/monobot/asyncorm
    :alt: Build status

.. image:: https://readthedocs.org/projects/asyncorm/badge/?version=development
    :target: http://asyncorm.readthedocs.io/en/development/
    :alt: Documentation Status



A fully asynchronous python ORM

* Free software: Apache Software License 2.0
* Documentation: https://asyncorm.readthedocs.io.


Features
--------

WARNING: version prebeta !!

WARNING: Work In Progress !!

**AsyncORM** is a fully async ORM_ inspired in the fantastic `django orm`_

.. _ORM: https://en.wikipedia.org/wiki/Object-relational_mapping
.. _django orm: https://docs.djangoproject.com/en/1.11/topics/db/

**AsyncORM** currently only supports postgres, but its developed to be "easy" to plug a number of different database interfaces.

It is designed to be used together with sanic_ or other async webserver.

.. _sanic: https://github.com/channelcat/sanic

To do
-----

A number of things are needed to be able to release asyncOrm a production ready ORM:

- better the documentation!
- migration support (forward migration at least)
- other databases interfaces ( `mysql`_ / `mariaDb`_ first priority)
- `prefetch_related`_ functionality
- Missing Field types: OneToOneField, DateTimeField (and rework DateField), `uuid4field`_

.. _mySql: https://www.mysql.com/
.. _mariaDb: https://mariadb.org/
.. _prefetch_related: https://docs.djangoproject.com/en/1.11/ref/models/querysets/#prefetch_related support
.. _uuid4field: https://www.postgresql.org/docs/9.5/static/datatype-uuid.html

Dependencies
------------

AsyncOrm currently only depends on AsyncPg.

asyncpg_, is a database interface library designed specifically for PostgreSQL and Python/asyncio.

.. _asyncpg: https://github.com/MagicStack/asyncpg

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
