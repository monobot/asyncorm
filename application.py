import importlib
# import inspect
import asyncio

from .exceptions import ModuleError

DEFAULT_CONFIG = {
    'db_config': None,
    'loop': asyncio.get_event_loop(),
    'manager': 'PostgresManager',
    'models': None,
}


class OrmApp(object):
    db_manager = None
    # models = None

    def configure(self, config):
        # models = config.pop('modules', None)
        # if models:
        #     self.models = self.get_models(models)

        DEFAULT_CONFIG.update(config)

        db_config = config.get('db_config', None)
        if not db_config:
            raise ModuleError(
                'Imposible to configure without database configuration!'
            )

        loop = DEFAULT_CONFIG.get('loop')
        db_config['loop'] = loop

        database_module = importlib.import_module('asyncorm.database')

        manager = getattr(database_module, 'PostgresManager')
        self.db_manager = manager(db_config)

        return config

    # def get_models(self, modules):
    #     # find classes, shove them in a {'name':object} dict
    #     from model import Model
    #     ret_list = []
    #     for m in modules:
    #         module = importlib.import_module(m)
    #         classes = dict(inspect.getmembers(
    #             module, predicate=lambda x: isinstance(x, Model))
    #         )
    #         print(classes)
    #     return ret_list


orm_app = OrmApp()


def configure_orm(config):
    global orm_app
    orm_app.configure(config)
    return orm_app
