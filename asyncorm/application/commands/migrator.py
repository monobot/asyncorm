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
        if self.args.app != '*' and self.args.app not in self.orm.apps.keys():
            raise CommandError('App not defined in the orm')
        if self.args.app == '*' and self.args.migration is not None:
            raise CommandError('Migration "{}" specified when the App is not'.format(self.args.migration))

    def configure_orm(self):
        config_filename = os.path.join(cwd, self.args.config[0])
        if not os.path.isfile(config_filename):
            raise CommandError('the configuration file does not exist')
        return configure_orm(config=config_filename)

    async def run(self):
        # create if not exists the migration table!!
        await AsyncormMigrations().objects.create_table()

        apps = self.args.app != '*' and [self.args.app] or [k for k in self.orm.apps.keys()]
        migration = self.args.migration != '?' and self.args.migration or None

        if self.args.command == 'makemigrations':
            args = (apps, )
        else:
            args = (apps, migration)
        await getattr(self, self.args.command)(*args)

    async def makemigrations(self, apps):
        logger.info('migrations')
        for module in [self.orm.apps[m] for m in apps]:
            pass

    async def migrate(self, apps, migration):
        logger.info('migrate')
        for module in [self.orm.apps[m] for m in apps]:
            await module.check_current_migrations_status(migration)
