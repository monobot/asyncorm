#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'asyncpg==0.14.0',
    'netaddr==0.7.19',
]

test_requirements = [
    'pip==9.0.1',
    'bumpversion==0.5.3',
    'wheel==0.30.0',
    'watchdog==0.8.3',
    'flake8==3.5.0',
    'tox==2.9.1',
    'coverage==4.4.2',
    'Sphinx==1.6.6',
    'asyncpg==0.14.0',
    'netaddr==0.7.19',
]

setup(
    name='asyncorm',
    version='0.3.8',
    description="A fully asynchronous python ORM",
    long_description=readme + '\n\n' + history,
    author="Héctor Alvarez (monobot)",
    author_email='monobot.soft@gmail.com',
    url='https://github.com/monobot/asyncorm',
    packages=['asyncorm', ],
    package_dir={'asyncorm': 'asyncorm'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='asyncorm',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'orm_setup=asyncorm.application.commands.orm_setup:setup',
        ],
    },
)
