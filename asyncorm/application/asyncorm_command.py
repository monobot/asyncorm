import argparse
import textwrap
from ..exceptions import CommandException

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent(
        '''\
    --------------------------------------------------------------------------
                     asyncorm migration management
    --------------------------------------------------------------------------

        > asyncorm makemigrations

            makemigrations, prepares the migration comparing the actual state
            in the database with the latest migration created

        > asyncorm migrate

            migrate, executes the pending migrations
            you can optionally specify what app  to migrate
            > asyncorm migrate library

            or even app and what specific migration name
            > asyncorm migrate library 0002

    --------------------------------------------------------------------------
        '''
    )
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

args = parser.parse_args()


if args.command == 'makemigrations' and args.app is not None:
    raise CommandException(
        'You can not specify the app when making migrations'
    )


def manage():
    print(args.command, args.app, args.migration)
