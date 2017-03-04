import importlib
import inspect
import asyncio

from .exceptions import ModuleError

DEFAULT_CONFIG = {
    'db_config': None,
    'loop': asyncio.get_event_loop(),
    'manager': 'PostgresManager',
    'modules': None,
}


class OrmApp(object):
    db_manager = None
    loop = None
    models = None

    def configure(self, config):
        self.models = self.get_models(config.pop('modules', None))

        DEFAULT_CONFIG.update(config)

        db_config = config.get('db_config', None)
        if not db_config:
            raise ModuleError(
                'Imposible to configure without database configuration!'
            )

        loop = DEFAULT_CONFIG.get('loop')
        db_config['loop'] = loop
        self.loop = loop

        database_module = importlib.import_module('asyncorm.database')

        manager = getattr(database_module, 'PostgresManager')
        self.db_manager = manager(db_config)

        self._set_database_manager()

        return config

    def get_models(self, modules):
        if modules is None:
            return None
        # find classes, save them in a {'name':object} dict
        from asyncorm.model import Model
        models = {}
        for m in modules:
            module = importlib.import_module('{}.models'.format(m))
            for k, v in inspect.getmembers(module):
                try:
                    if issubclass(v, Model):
                        models.update({k: v})
                except TypeError:
                    pass
        return models

    def _set_database_manager(self):
        for model in self.models.values():
            model._set_database_manager(self.db_manager)


orm_app = OrmApp()


def configure_orm(config):
    global orm_app
    orm_app.configure(config)
