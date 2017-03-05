import importlib
import inspect
import asyncio

from collections import OrderedDict

from .exceptions import ModuleError
from .fields import ForeignKey, ManyToMany

DEFAULT_CONFIG = {
    'db_config': None,
    'loop': asyncio.get_event_loop(),
    'manager': 'PostgresManager',
    'modules': None,
}


class OrmApp(object):
    db_manager = None
    loop = None
    models = OrderedDict()

    def configure(self, config):
        self.get_models(config.pop('modules', None))

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
        for m in modules:
            module = importlib.import_module('{}.models'.format(m))
            for k, v in inspect.getmembers(module):
                try:
                    if issubclass(v, Model) and v is not Model:
                        self.models[k] = v
                except TypeError:
                    pass
        self._models_configure()

    def _models_configure(self):
        for name, model in self.models.items():
            for f in model.fields.values():
                if isinstance(f, ManyToMany):
                    pass
                    # print(name, 'has m2m:', f.field_name,
                    #     self.get_model(f.foreign_key))
                elif isinstance(f, ForeignKey):
                    self.get_model(f.foreign_key)._set_reverse_foreignkey(name)
                    # print(name, 'has fk:', f.field_name,
                    #     self.get_model(f.foreign_key))

    def _set_database_manager(self):
        for model in self.models.values():
            model._set_database_manager(self.db_manager)

    def get_model(self, model_name):
        if self.models is None:
            raise ModuleError('There are no modules declared in the orm')

        try:
            return self.models[model_name]
        except KeyError:
            raise ModuleError('The model does not exists')


orm_app = OrmApp()


def configure_orm(config):
    global orm_app
    orm_app.configure(config)
    return orm_app
