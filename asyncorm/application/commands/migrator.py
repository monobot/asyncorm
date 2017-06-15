import argparse
import textwrap
import os

from ..configure import configure_orm
from ...exceptions import CommandException

cwd = os.getcwd()

help_text = '''
-------------------------------------------------------------------------------
                         asyncorm migration management
-------------------------------------------------------------------------------

    > asyncorm makemigrations

        makemigrations, prepares the migration comparing the actual state
        in the database with the latest migration created

    > asyncorm migrate

        migrate, executes the pending migrations
        you can optionally specify what app  to migrate
        > asyncorm migrate library

        or even app and what specific migration name
        > asyncorm migrate library 0002

-------------------------------------------------------------------------------
help_text = '''

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent(help_text)
)

parser.add_argument(
    'command', type=str, choices=('makemigrations', 'migrate'),
    help=('makemigrations or migrate')
)

parser.add_argument(
    'app', type=str, nargs='?',
    help=('app you want to migrate')
)

parser.add_argument(
    'migration', type=str, nargs='?',
    help=('migration_name you want the app to migrate to')
)

parser.add_argument(
    '--config', type=str, nargs=1, default=['asyncorm.ini', ],
    help=('configuration file (defaults to asyncorm.ini)')
)

args = parser.parse_args()

# check that the arguments are correctly sent
if args.command == 'makemigrations' and args.app is not None:
    raise CommandException(
        'You can not specify the app when making migrations'
    )

config_filename = os.path.join(cwd, args.config[0])
if not os.path.isfile(config_filename):
    raise CommandException(
        'the configuration file does not exist'
    )


def migrator():
    configure_orm(config=config_filename)
