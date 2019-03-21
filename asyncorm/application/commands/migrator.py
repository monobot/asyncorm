import argparse
import logging
import os
import textwrap

from asyncorm.application.configure import DEFAULT_CONFIG_FILE, configure_orm
from asyncorm.exceptions import AsyncOrmCommandError, AsyncOrmMigrationError
from asyncorm.migrations.models import AsyncormMigrations
from asyncorm.orm_migrations.migration_constructor import MigrationConstructor

cwd = os.getcwd()

logger = logging.getLogger("asyncorm_stream")

help_text = """\
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
"""


class Migrator(object):
    MAKEMIGRATIONS = "makemigrations"
    MIGRATE = "migrate"
    DATAMIGRATION = "datamigration"
    SHOWMIGRATIONS = "showmigrations"
    ALL_APPS = ["*"]

    def __init__(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent(help_text)
        )

        parser.add_argument(
            "command",
            type=str,
            choices=(self.MAKEMIGRATIONS, self.MIGRATE, self.DATAMIGRATION, self.SHOWMIGRATIONS),
            help=("makemigrations, migrate, datamigration or showmigrations"),
        )

        parser.add_argument(
            "apps", type=str, nargs="?", default=self.ALL_APPS, help=("app the command will be aplied to")
        )

        parser.add_argument("migration", type=str, nargs="?", help=("migration_name you want the app to migrate to"))

        parser.add_argument(
            "--initial",
            type=self.initial_parse,
            nargs="?",
            default="false",
            help=("Mark as initial when its the initial (first) migration for the app."),
        )

        parser.add_argument(
            "--config",
            type=str,
            nargs=1,
            default=[DEFAULT_CONFIG_FILE],
            help=("configuration file (defaults to asyncorm.ini in the same " "directory)"),
        )

        self.args = parser.parse_args()
        self.orm = self.configure_orm()

        # allows multiple apps comma separated
        if self.args.apps != self.ALL_APPS:
            self.args.apps = self.args.apps.split(",")

        self.check_args()

    @staticmethod
    def initial_parse(initial):
        if initial.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif initial.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    def check_args(self):
        if self.args.apps != self.ALL_APPS:
            for app in self.args.apps:
                if app not in self.orm.apps.keys():
                    raise AsyncOrmCommandError('App "{}" not defined in the orm'.format(app))

        if self.args.apps == self.ALL_APPS and self.args.migration is not None:
            raise AsyncOrmCommandError('Migration "{}" specified when the App is not'.format(self.args.migration))
        if self.args.initial and self.args.command == self.MIGRATE:
            raise AsyncOrmCommandError('You can not migrate "initial". try "makemigrations"')
        if self.args.command == self.MAKEMIGRATIONS and self.args.migration is not None:
            raise AsyncOrmCommandError('Migration "{}" specified when "makemigrations"'.format(self.args.migration))
        if self.args.command == self.DATAMIGRATION and self.args.apps == self.ALL_APPS:
            raise AsyncOrmCommandError("Datamigration requires an app defined")
        if self.args.command == self.SHOWMIGRATIONS and self.args.migration is not None:
            raise AsyncOrmCommandError('Migration "{}" specified when "showmigrations"'.format(self.args.migration))

    def configure_orm(self):
        config_filename = os.path.join(cwd, self.args.config[0])
        if not os.path.isfile(config_filename):
            raise AsyncOrmCommandError("the configuration file does not exist")
        return configure_orm(config=config_filename)

    async def run(self):
        # creates the migration table if does'nt exist!!
        await AsyncormMigrations().objects.create_table()

        apps = self.args.apps if self.args.apps != self.ALL_APPS else [k for k in self.orm.apps.keys()]
        migration = self.args.migration != "?" and self.args.migration or None

        if self.args.command in (self.MAKEMIGRATIONS, self.SHOWMIGRATIONS):
            args = (apps,)
        else:
            args = (apps, migration)
        await getattr(self, self.args.command)(*args)

    async def makemigrations(self, apps):
        """Creates the file that can be used to migrate the table from a state to the next."""
        logger.info("migrations for %s", apps)
        for app in [self.orm.apps[m] for m in apps]:
            logger.info('##### checking models for "%s" #####', app.name)
            try:
                _migration_status = await app._construct_migrations_status()
                _latest_fs_declared = _migration_status["_latest_fs_declared"]
                logger.info(_latest_fs_declared)
                initial = self.args.initial
                if not initial and not _latest_fs_declared:
                    raise AsyncOrmMigrationError(
                        'No migration defined in filesystem for app "{}" '
                        "and makemigration not marked as initial.".format(app.name)
                    )

                if initial and _latest_fs_declared:
                    raise AsyncOrmMigrationError(
                        "Makemigrations marked as initial where there is already an initial " "migration declared."
                    )

                file_name = app._next_fs_migration_name(stage="initial" if initial else "auto")
                MigrationConstructor(
                    app._get_absolute_migration("{}.py".format(file_name)),
                    app._get_migration_depends(),
                    app._get_migration_actions(),
                    initial=True,
                )
            except AsyncOrmMigrationError:
                logger.exception("Migration Error")

    async def migrate(self, apps, migration):
        """Migrates the database from an state to the next using the migration files defined."""
        logger.info("migrate %s %s", apps, migration if migration else "")
        for module in [self.orm.apps[m] for m in apps]:
            await module._check_current_migrations_status(migration)

    async def datamigration(self, apps, migration):
        """ Creates an empty migration file, so the user can create their own migration."""
        logger.info("datamigration %s %s", apps, migration)

    async def showmigrations(self, apps):
        """Shows the list of migrations defined in the filesystem and its status in database."""
        for app in [self.orm.apps[m] for m in apps]:
            logger.info('%s\n Migration list for "%s" app\n%s', "~" * 50, app.name, "-" * 50)
            _migration_status = await app._construct_migrations_status()
            for mig_name in [k for k in _migration_status.keys() if not k.startswith("_")]:
                logger.info(" [%s] %s", "x" if _migration_status[mig_name]["migrated"] else " ", mig_name)
            logger.info("%s\n", "~" * 50)
