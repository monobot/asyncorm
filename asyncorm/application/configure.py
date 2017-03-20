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
        '''
        Configures the system:
        get all the models declared
        sets the database configured and adds the loop

        Then the database manager is configured, and set to all the
        models previously declared
        and then we finish the models configurations using
        _models_configure(): will take care of the inverse relations for
        foreignkeys and many2many
        '''
        self.get_declared_models(config.pop('modules', None))

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

        # After the manager is set then we can build the rest of db features
        self._models_configure()

    def get_declared_models(self, modules):
        if modules is None:
            return None

        from asyncorm.model import Model
        for m in modules:
            module = importlib.import_module('{}.models'.format(m))
            for k, v in inspect.getmembers(module):
                try:
                    if issubclass(v, Model) and v is not Model:
                        self.models[k] = v
                except TypeError:
                    pass

    def get_model(self, model_name):
        if self.models is None:
            raise ModuleError('There are no modules declared in the orm')

        try:
            return self.models[model_name]
        except KeyError:
            raise ModuleError('The model does not exists')

    def _models_configure(self):
        # and we set it to all the different models defined
        self._set_model_orm()

        for name, model in self.models.items():

            for n, f in model.fields.items():
                if isinstance(f, ManyToMany):
                    m2m_tablename = '{}_{}'.format(name, f.foreign_key).lower()
                    other = self.get_model(f.foreign_key)
                    other._set_many2many(f, m2m_tablename, f.foreign_key, name)

                    model._set_many2many(f, m2m_tablename, name, f.foreign_key,
                                         # direct=True
                                         )

                elif isinstance(f, ForeignKey):
                    other_model = self.get_model(f.foreign_key)
                    other_model._set_reverse_foreignkey(name, f.field_name)

    def _set_model_orm(self):
        for model in self.models.values():
            model._set_orm(self)

    async def create_db(self):
        """
        We  create all tables for each of the declared models
        """

        for model in self.models.values():
            await model().objects._create_table()

        for model in self.models.values():
            await model().objects._add_fk_columns()

        for model in self.models.values():
            await model().objects._add_m2m_columns()

        for model in self.models.values():
            await model().objects._unique_together()

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
