import inspect
import importlib
import logging
import os

logger = logging.getLogger('asyncorm')


class Module(object):
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

    @staticmethod
    def migration_integer_number(migration_name):

        return int(migration_name.split('__')[0])

    async def latest_db_migration(self):
        kwargs = {
            'select': 'name',
            'table_name': 'asyncorm_migrations',
            'join': '',
            'ordering': 'ORDER BY  -id',
            'condition': "app = '{}'".format(self.name)
        }

        result = await self.db_manager.request(self.db_manager.db__select.format(**kwargs))
        return result and self.migration_integer_number(result['name']) or None

    def latest_fs_migration(self):
        python_ext = '.py'
        migrations_dir = os.path.join(self.dir_name, 'migrations')
        os.makedirs(migrations_dir, exist_ok=True)
        filenames = [fn for fn in next(os.walk(migrations_dir))[2] if fn[-3:] == python_ext]

        return filenames and self.migration_integer_number(sorted(filenames)[-1].rstrip(python_ext)) or None
