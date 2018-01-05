import hashlib
import importlib
import inspect
import logging
import os
from datetime import datetime

from asyncorm.exceptions import MigrationError

logger = logging.getLogger('asyncorm')


class App(object):
    def __init__(self, relative_name, db_manager):
        self.dir_name = False
        self.relative_name = relative_name
        self.name = relative_name.split('.')[-1]
        self.models = self.get_declared_models()

        self.db_manager = db_manager

    def get_declared_models(self):
        # this import should be here otherwise causes circular import
        from asyncorm import models

        _models = {}
        try:
            module = importlib.import_module('{}.models'.format(self.relative_name))
        except ImportError:
            logger.error('unable to import {}'.format(self.relative_name))

        for k, v in inspect.getmembers(module):
            try:
                if issubclass(v, models.Model) and v is not models.Model:
                    _models[k] = v
                    _models.update({k: v})

                    self.dir_name = self.dir_name or v().dir_name
            except TypeError:
                pass
        return _models

    def check_migration_dir(self):
        self.migrations_dir = os.path.join(self.dir_name, 'migrations')
        os.makedirs(self.migrations_dir, exist_ok=True)

    async def check_makemigrations_status(self):
        """ Checks that the migration is correcly synced and everything is fine
        returns the latest migration applied file_name
        """
        latest_fs_migration = self.latest_fs_migration()
        latest_db_migration = await self.latest_db_migration()
        latest_fs_migration_number = self.migration_integer_number(latest_fs_migration)
        latest_db_migration_number = self.migration_integer_number(latest_db_migration)

        logger.info('\n\n\n\n{} {}\n\n'.format(latest_fs_migration, latest_db_migration))
        # the database doesn't have any migration
        if not latest_db_migration:
            if latest_fs_migration:
                raise MigrationError(
                    'The model is not in the latest filesystem status, so the migration created will '
                    'not be consistent.\nPlease "migrate" the database before "makemigrations" again.'
                )
        else:
            if not latest_fs_migration:
                raise MigrationError(
                    'Severe inconsistence detected, the database has at least one migration applied and no '
                    'migration described in the filesystem.')
            if latest_db_migration_number > latest_fs_migration_number:
                raise MigrationError(
                    'There is an inconsistency, the database has a migration named "{}" '
                    'more advanced than the filesystem "{}"'.format(
                        latest_db_migration,
                        latest_fs_migration,
                    )
                )

            elif latest_db_migration_number < latest_fs_migration_number:
                raise MigrationError(
                    'The model is not in the latest filesystem status, so the migration created will '
                    'not be consistent.\nPlease "migrate" the database before "makemigrations" again.'
                )
            elif latest_fs_migration != latest_db_migration:
                raise MigrationError(
                    'The migration in the filesystem "{}" is not the same migration '
                    'applied in the database "{}" .'.format(
                        latest_fs_migration,
                        latest_db_migration,
                    )
                )
        return latest_fs_migration

    async def check_current_migrations_status(self, target):
        self.check_migration_dir()
        latest_db_migration = self.migration_integer_number(await self.latest_db_migration())

        forward = False
        if target is None:
            target_fs_migration = self.migration_integer_number(self.latest_fs_migration())
        else:
            target_fs_migration = [
                fn for fn in next(os.walk(self.migrations_dir))[2] if fn.startswith(target)]
        if not target_fs_migration:
            raise MigrationError('the migration {} does not exist for app {}'.format(target, self.name))

        if latest_db_migration is not None and target_fs_migration is not None:
            if latest_db_migration > target_fs_migration:
                raise MigrationError(
                    'There is an inconsistency, the database has a migration named "{}" '
                    'more advanced than the filesystem "{}"'.format(
                        latest_db_migration,
                        target_fs_migration,
                    )
                )
            if latest_db_migration < target_fs_migration:
                forward = True
        return forward

    @staticmethod
    def migration_integer_number(migration_name):
        return migration_name and int(migration_name.split('__')[0]) or 0

    async def latest_db_migration(self):
        kwargs = {
            'select': 'name',
            'table_name': 'asyncorm_migrations',
            'join': '',
            'ordering': 'ORDER BY -id',
            'condition': "app = '{}'".format(self.name)
        }

        result = await self.db_manager.request(self.db_manager.db__select.format(**kwargs))
        return result and result['name'] or 0

    def latest_fs_migration(self):
        python_ext = '.py'
        self.check_migration_dir()
        filenames = [fn for fn in next(os.walk(self.migrations_dir))[2] if fn[-3:] == python_ext]

        return filenames and sorted(filenames)[-1].rstrip(python_ext) or 0

    def next_fs_migration_name(self, stage='auto'):
        if stage not in ('auto', 'data', 'initial'):
            raise MigrationError('that migration stage is not supported')
        target_fs_migration = self.migration_integer_number(self.latest_fs_migration())
        random_hash = hashlib.sha1()
        random_hash.update('{}{}'.format(target_fs_migration, str(datetime.now())).encode('utf-8'))
        return '{}__{}_{}'.format(
            '0000{}'.format(target_fs_migration + 1)[-5:],
            stage,
            random_hash.hexdigest(),
        )[:26]
