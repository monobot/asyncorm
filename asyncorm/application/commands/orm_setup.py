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


-------------------------------------------------------------------------------
        '''
    )
)
parser.add_argument(
    'command', type=str, choices=('setup', ),
    help=('sets up the manage command and asyncorm.ini in the same diectory')
)

ini = """
[db_config]
database =
host =
user =
password =

[orm]
modules =

"""

man = """
from asyncorm.application.commands.migrator import migrator


migrator()
"""


def file_creator(filename):
    data_dict = {
        'asyncorm.ini': ini,
        'orm_migrator.py': man,
    }
    file_path = os.path.join(os.getcwd(), filename)
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write(data_dict[filename])


def setup():
    file_creator('asyncorm.ini')
    file_creator('orm_migrator.py')
