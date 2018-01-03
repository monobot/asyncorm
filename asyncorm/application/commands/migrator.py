import argparse
import logging
import os
import textwrap

from asyncorm.application.configure import configure_orm, DEFAULT_CONFIG_FILE
from asyncorm.exceptions import CommandError
from asyncorm.models.migrations.constructor import MigrationConstructor
from asyncorm.models.migrations.models import AsyncormMigrations
from asyncpg.exceptions import UndefinedTableError

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
        self.check_args()

        self.orm = self.configure_orm()

    def check_args(self):
        # check that the arguments are correctly sent
        if self.args.command == 'makemigrations' and self.args.app != '*':
            raise CommandError('You can not specify the app when making migrations')

    def configure_orm(self):
        config_filename = os.path.join(cwd, self.args.config[0])
        if not os.path.isfile(config_filename):
            raise CommandError('the configuration file does not exist')
        return configure_orm(config=config_filename)

    async def run(self):
        # create if not exists the migration table!!
        await AsyncormMigrations().objects.create_table()

        if self.args.app != '*':
            if self.args.app not in self.orm.modules.keys():
                raise CommandError('Module not defined in the orm')

        for module_name in self.orm.modules.keys():
            try:
                models_dict = {}
                required_migration = False

                for model_name in self.orm.modules[module_name]:
                    model = self.orm.get_model(model_name)

                    latest_db_migration = await model().latest_db_migration()
                    latest_db_migration = latest_db_migration and latest_db_migration.split(' ')[0] or 0

                    latest_fs_migration = model().latest_fs_migration()
                    latest_fs_migration = latest_fs_migration and latest_fs_migration.split(' ')[0] or 0

                    next_fs_migration = os.path.join(
                        model().migrations_dir,
                        '{}.py'.format(model().next_fs_migration())
                    )

                    models_dict[model_name] = model.current_state()

                    if not latest_fs_migration:
                        if not latest_db_migration:
                            logger.debug(
                                'No migration exists for app "{}", creating initial one.'.format(
                                    module_name))
                            required_migration = True
                        else:
                            logger.debug(
                                'Impossible to solve inconsistency; there is no migration file'
                                'but there is a migration {} in the database for app "{}"'.format(
                                    latest_db_migration,
                                    module_name))
                            pass
                    else:
                        if not latest_db_migration:
                            # migration not applied
                            pass
                        elif int(latest_fs_migration) > int(latest_db_migration):
                            pass
                        elif int(latest_fs_migration) < int(latest_db_migration):
                            pass

                if required_migration:
                    mc = MigrationConstructor(next_fs_migration)
                    mc.set_models(models_dict)

            except UndefinedTableError:
                logger.error('asyncorm raised "UndefinedTableError" in app "{}"'.format(module_name))

        command = getattr(self, self.args.command)
        command()

    @staticmethod
    def makemigrations():
        print('makemigrations')

    @staticmethod
    def migrate():
        print('migrate')
