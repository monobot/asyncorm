========
asyncOrm
========

[![Pypi package](https://img.shields.io/pypi/v/asyncorm.svg)](https://pypi.python.org/pypi/asyncorm) [![Python versions](https://img.shields.io/pypi/pyversions/asyncorm.svg)](https://pypi.python.org/pypi/asyncorm) [![build status](https://travis-ci.org/monobot/asyncorm.svg?branch=development)](https://travis-ci.org/monobot/asyncorm) [![Code quality](https://api.codacy.com/project/badge/Grade/86ee891909654fc0a294849d0a436109)](https://www.codacy.com/app/monobot/asyncorm?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=monobot/asyncorm&amp;utm_campaign=Badge_Grade) [![Coverage](https://api.codacy.com/project/badge/Coverage/86ee891909654fc0a294849d0a436109)](https://www.codacy.com/app/monobot/asyncorm?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=monobot/asyncorm&amp;utm_campaign=Badge_Coverage) [![Packages status](https://pyup.io/repos/github/monobot/asyncorm/shield.svg)](https://pyup.io/account/repos/github/monobot/asyncorm/) [![Build status](https://travis-ci.org/monobot/asyncorm.svg?branch=development)](https://travis-ci.org/monobot/asyncorm) [![Documentation Status](https://readthedocs.org/projects/asyncorm/badge/?version=development)](http://asyncorm.readthedocs.io/en/development/) [![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

A fully asynchronous python ORM

-   Free software: Apache Software License 2.0
-   Documentation: <https://asyncorm.readthedocs.io>.

Features
========

WARNING: version prebeta !!

WARNING: Work In Progress !!

**AsyncORM** is a fully async [ORM](https://en.wikipedia.org/wiki/Object-relational_mapping) inspired by the fantastic [django orm](https://docs.djangoproject.com/en/1.11/topics/db/)

**AsyncORM** currently only supports postgres, but its developed to be
"easy" to plug a number of different database interfaces.

It is designed to be used with any async library, but with
[sanic](https://github.com/channelcat/sanic) in mind.

To do
=====

A number of things are needed to be able to release asyncOrm as a
production ready ORM:

-   better the documentation!
-   migration support (forward migration at least)
-   other databases interfaces ( [mysql](https://www.mysql.com/) /
    [mariaDb](https://mariadb.org/) first priority)
-   [prefetch\_related](https://docs.djangoproject.com/en/1.11/ref/models/querysets/#prefetch_related%20support)
    functionality
-   Missing Field types: OneToOneField

Dependencies
============

AsyncOrm currently only depends on AsyncPg and netaddr.

[asyncpg](https://github.com/MagicStack/asyncpg), is a database
interface library designed specifically for PostgreSQL and
Python/asyncio.

[netaddr](https://github.com/drkjam/netaddr), A network address
manipulation library for Python
