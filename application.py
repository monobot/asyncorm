import importlib
import inspect

from exceptions import ModuleError
from database import PostgresManager

default_config = {'db_config': None}


class OrmApp(object):

    def __init__(self, config):
        self.models = self.get_models(config.pop['modules'])

        config = self.configure(config)
        self.db = PostgresManager(config['db_config'])

    def configure(self, config):
        default_config.update(config)

        db_config = config.get('db_config', None)
        if not db_config:
            raise ModuleError(
                'Imposible to configure without database configuration!'
            )

        loop = config.get('loop', None)
        if not loop:
            raise ModuleError(
                'Imposible to configure without main loop!'
            )
        db_config['loop'] = loop

        dm = PostgresManager(db_config)
        config.update({'dm': dm})

        return config

    def get_models(self, modules):
        # find classes, shove them in a {'name':object} dict
        ret_list = []
        for model in modules:
            model = importlib.import_module('matplotlib.text')
            classes = dict(inspect.getmembers(
                model, predicate=lambda x: isinstance(x, type))
            )
            print(classes)
        return ret_list
