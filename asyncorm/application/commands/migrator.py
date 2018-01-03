import argparse
import logging
import os
import textwrap

from asyncorm.application.configure import configure_orm, DEFAULT_CONFIG_FILE
from asyncorm.exceptions import CommandError
# from asyncorm.models.migrations.constructor import MigrationConstructor
from asyncorm.models.migrations.models import AsyncormMigrations
# from asyncpg.exceptions import UndefinedTableError

cwd = os.getcwd()

logger = logging.getLogger('asyncorm')

help_text = '''\
-------------------------------------------------------------------------------
                         asyncorm migration management
-------------------------------------------------------------------------------

    > asyncorm makemigrations

        Prepares the migration comparing the actual state
        in the database with the latest migration created

    > asyncorm migrate

        Executes the pending migrations
        you can optionally specify what app  to migrate
        > asyncorm migrate library

        or even app and what specific migration number you want to go to
        forwards and backwards
        > asyncorm migrate library 00002

-------------------------------------------------------------------------------
'''


class Migrator(object):

    def __init__(self):
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
            '--config', type=str, nargs=1, default=[DEFAULT_CONFIG_FILE, ],
            help=(
                'configuration file (defaults to asyncorm.ini in the same '
                'directory)'
            )
        )

        self.args = parser.parse_args()
        self.orm = self.configure_orm()

        self.check_args()

    def check_args(self):
        # check that the arguments are correctly sent
        if self.args.app != '*' and self.args.app not in self.orm.modules.keys():
            raise CommandError('Module not defined in the orm')

    def configure_orm(self):
        config_filename = os.path.join(cwd, self.args.config[0])
        if not os.path.isfile(config_filename):
            raise CommandError('the configuration file does not exist')
        return configure_orm(config=config_filename)

    async def run(self):
        # create if not exists the migration table!!
        await AsyncormMigrations().objects.create_table()

        if self.args.app != '*':
            modds = [self.args.app]
        else:
            modds = [k for k in self.orm.modules.keys()]

        for mod in modds:
            mod = self.orm.modules[mod]

            latest_db_migration = await mod.latest_db_migration()
            latest_fs_migration = mod.latest_fs_migration()

            print('latest_db_migration', latest_db_migration)
            print('latest_fs_migration', latest_fs_migration)

        command = getattr(self, self.args.command)
        command()

    def makemigrations(self):
        logger.info('makemigrations')

    def migrate(self):
        logger.info('migrate')
