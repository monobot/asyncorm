import argparse
import textwrap
import os

cwd = os.getcwd()

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent(
        '''
-------------------------------------------------------------------------------
                                asyncorm setup
-------------------------------------------------------------------------------

    asyncorm setup

-------------------------------------------------------------------------------
        '''
    )
)

parser.add_argument(
    'command', type=str, choices=('setup', ),
    help=(
        'sets up the orm_migrator.py command and also an empty asyncorm.ini '
        'in the same directory')
)

args = parser.parse_args()

ini = """\
[db_config]
database =
host =
user =
password =

[orm]
modules =

"""

man = """\
import asyncio

from asyncorm.application.commands.migrator import Migrator

loop = asyncio.get_event_loop()

migrator = Migrator()
task = loop.create_task(migrator.run())
loop.run_until_complete(asyncio.gather(task))
"""


def file_creator(filename):
    content_dict = {'asyncorm.ini': ini, 'orm_migrator.py': man}
    file_path = os.path.join(os.getcwd(), filename)

    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write(content_dict[filename])


def setup():
    file_creator('asyncorm.ini')
    file_creator('orm_migrator.py')
