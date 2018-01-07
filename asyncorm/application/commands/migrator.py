import argparse
import logging
import os
import textwrap

from asyncorm.application.configure import configure_orm, DEFAULT_CONFIG_FILE
from asyncorm.exceptions import CommandError, MigrationError
# from asyncorm.orm_migrations.migrations.constructor import MigrationConstructor
from asyncorm.orm_migrations.models import AsyncormMigrations
# from asyncpg.exceptions import UndefinedTableError

cwd = os.getcwd()

logger = logging.getLogger('asyncorm_stream')

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
            'command', type=str, choices=('makemigrations', 'migrate', 'datamigration', 'showmigrations'),
            help=('makemigrations, migrate, datamigration or showmigrations')
        )

        parser.add_argument(
            'app', type=str, nargs='?', default='*',
            help=('app the command will be aplied to')
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
        if self.args.app != '*' and self.args.app not in self.orm.apps.keys():
            raise CommandError('App not defined in the orm')
        if self.args.app == '*' and self.args.migration is not None:
            raise CommandError('Migration "{}" specified when the App is not'.format(self.args.migration))
        if self.args.command == 'makemigrations' and self.args.migration is not None:
            raise CommandError('Migration "{}" specified when "makemigrations"'.format(self.args.migration))
        if self.args.command == 'datamigration' and self.args.app == '*':
            raise CommandError('Datamigration requires an app defined')
        if self.args.command == 'showmigration' and self.args.migration is not None:
            raise CommandError('Migration "{}" specified when "showmigrations"'.format(self.args.migration))

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

        if self.args.command in ('makemigrations', 'showmigrations'):
            args = (apps, )
        else:
            args = (apps, migration)
        await getattr(self, self.args.command)(*args)

    async def makemigrations(self, apps):
        """ Creates the file that can be used to migrate the table from a state to the next
        """
        logger.info('migrations for {}'.format(apps))
        for app in [self.orm.apps[m] for m in apps]:
            logger.info('checking models for {}'.format(app.name))
            try:
                latest_fs_migration = await app.check_makemigrations_status()
                logger.info(latest_fs_migration)
                migration = app.get_migration(latest_fs_migration).Migration()
            except MigrationError as e:
                logger.error('\nMigration Error: {}\n'.format(e))

    async def migrate(self, apps, migration):
        """ Migrates the database from an state to the next using the migration files defined
        """
        logger.info('migrate {} {}'.format(apps, migration))
        for module in [self.orm.apps[m] for m in apps]:
            await module.check_current_migrations_status(migration)

    async def datamigration(self, apps, migration):
        """ Creates an empty migration file, so the user can create their own migration
        """
        logger.info('datamigration {} {}'.format(apps, migration))

    async def showmigrations(self, apps):
        """ Creates an empty migration file, so the user can create their own migration
        """
        for app in [self.orm.apps[m] for m in apps]:
            logger.info('{}\n Migration list for "{}" app\n{}\n'.format('~' * 50, app.name, '~' * 50, ))
            for mig_name in app.fs_migration_list():
                applied = await app.check_migration_applied(mig_name)
                logger.info(' [{}] {}'.format(applied and 'x' or ' ', mig_name))
            logger.info('\n')
