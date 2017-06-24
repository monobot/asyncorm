import argparse
import logging
import os
import textwrap

from asyncpg.exceptions import UndefinedTableError
from asyncorm.models.migrations.models import AsyncormMigrations
from asyncorm.models.migrations.constructor import MigrationConstructor

from ..configure import configure_orm
from ...exceptions import CommandError, MigrationError

cwd = os.getcwd()

logger = logging.getLogger('asyncorm')

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
    'app', type=str, nargs='?', default='*',
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
if args.command == 'makemigrations' and args.app != '*':
    raise CommandError(
        'You can not specify the app when making migrations'
    )

config_filename = os.path.join(cwd, args.config[0])
if not os.path.isfile(config_filename):
    raise CommandError(
        'the configuration file does not exist'
    )

orm = configure_orm(config=config_filename)


async def migrator():
    # create if not exists the migration table!!
    await AsyncormMigrations().objects.create_table()

    if args.app != '*':
        if args.app not in orm.modules.keys():
            raise CommandError('Module not defined in the orm')

    for module_name in orm.modules.keys():
        try:
            models_dict = {}
            for model_name in orm.modules[module_name]:
                model = orm.get_model(model_name)

                latest_db_migration = await model().latest_db_migration()
                latest_fs_migration = model().latest_fs_migration()

                db_migration_isNone = latest_db_migration is None
                fs_migration_isNone = latest_fs_migration is None

                if fs_migration_isNone and not db_migration_isNone:
                    raise MigrationError(
                        'Database with migrations not represented in the '
                        'migration files'
                    )

                if not db_migration_isNone and not fs_migration_isNone:
                    if int(latest_db_migration) > int(latest_fs_migration):
                        raise MigrationError(
                            'Database with migrations not represented in the '
                            'migration files'
                        )

                models_dict[model_name] = model.current_state()

            next_fs_migration = os.path.join(
                model().migrations_dir,
                '{}.py'.format(model().next_fs_migration())
            )
            mc = MigrationConstructor(next_fs_migration)
            mc.set_models(models_dict)

        except UndefinedTableError:
            logger.error(
                'asyncorm raised "UndefinedTableError" in app "{}"'.format(
                    module_name
                )
            )
