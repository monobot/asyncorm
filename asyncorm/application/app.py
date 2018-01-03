import inspect
import importlib
import logging
import os

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

    async def check_current_migrations_status(self, target):
        self.check_migration_dir()
        latest_db_migration = self.migration_integer_number(await self.latest_db_migration())

        if target is None:
            target_fs_migration = self.migration_integer_number(self.latest_fs_migration())
        else:
            target_fs_migration = [
                fn for fn in next(os.walk(self.migrations_dir))[2] if fn.startswith(target)]
            if not target_fs_migration:
                raise MigrationError('the migration {} does not exist for app {}'.format(target, self.name))

        if latest_db_migration is not None and target_fs_migration is not None:
            if latest_db_migration > target_fs_migration:
                pass
            if latest_db_migration < target_fs_migration:
                pass

    @staticmethod
    def migration_integer_number(migration_name):
        return migration_name and int(migration_name.split('__')[0]) or None

    async def latest_db_migration(self):
        kwargs = {
            'select': 'name',
            'table_name': 'asyncorm_migrations',
            'join': '',
            'ordering': 'ORDER BY -id',
            'condition': "app = '{}'".format(self.name)
        }

        result = await self.db_manager.request(self.db_manager.db__select.format(**kwargs))
        return result and result['name'] or None

    def latest_fs_migration(self):
        python_ext = '.py'
        self.check_migration_dir()
        filenames = [fn for fn in next(os.walk(self.migrations_dir))[2] if fn[-3:] == python_ext]

        return filenames and sorted(filenames)[-1].rstrip(python_ext) or None
