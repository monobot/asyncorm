#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='asyncorm',
    version='0.3.1',
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
            'asyncorm=asyncorm.application.commands.orm_setup:setup',
        ],
    },
)
