import importlib
import inspect
import asyncio

from collections import OrderedDict

from ..exceptions import ModuleError
from ..fields import ForeignKey, ManyToMany

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

        db_config['loop'] = self.loop = DEFAULT_CONFIG.get('loop')

        database_module = importlib.import_module('asyncorm.database')

        # we get the manager defined in the config file
        manager = getattr(database_module, DEFAULT_CONFIG['manager'])
        self.db_manager = manager(db_config)

        # and we set it to all the different models defined
        self._set_database_manager()

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
                    other_model = self.get_model(f.foreign_key)
                    other_model._set_manytomany(
                        '{}_{}'.format(name, f.foreign_key).lower(),
                        f.foreign_key,
                        name,
                    )

                    model._set_manytomany(
                        '{}_{}'.format(name, f.foreign_key).lower(),
                        name,
                        f.foreign_key,
                    )

                elif isinstance(f, ForeignKey):
                    other_model = self.get_model(f.foreign_key)
                    other_model._set_reverse_foreignkey(name, f.field_name)

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

    async def create_db(self):
        """
        We  create all tables for each of the declared models
        """
        queries = []
        delayed = []

        for model in self.models.values():
            queries.append(
                'DROP TABLE IF EXISTS {table} CASCADE'.format(
                    table=model().table_name
                )
            )
            queries.append(model.objects._creation_query())

            m2m_queries = model.objects._get_m2m_field_queries()
            if m2m_queries:
                delayed.append(m2m_queries)

        await self.db_manager.transaction_insert(queries + delayed)

    def sync_db(self):
        self.loop.run_until_complete(
            asyncio.gather(self.loop.create_task(self.create_db()))
        )


orm_app = OrmApp()


def configure_orm(config):
    # configure and return the already configured orm
    global orm_app
    orm_app.configure(config)
    return orm_app


def get_model(model_name):
    # wrapper around the orm method
    return orm_app.get_model(model_name)
