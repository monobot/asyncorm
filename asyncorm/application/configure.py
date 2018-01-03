import asyncio
import configparser
import importlib
import logging
import os

from asyncorm.exceptions import ConfigError, ModuleError, ModelError
from asyncorm.application.module import Module

logger = logging.getLogger('asyncorm')

DEFAULT_CONFIG = {
    'db_config': None,
    'loop': asyncio.get_event_loop(),
    'manager': 'PostgresManager',
    'modules': None,
}

DEFAULT_CONFIG_FILE = 'asyncorm.ini'


class OrmApp(object):
    db_manager = None
    loop = None
    models = {}
    modules = {}

    def configure(self, config):
        '''
        Configures the system:
        get all the models declared
        sets the database configured and adds the loop

        Then the database manager is configured, and set to all the
        models previously declared
        and then we finish the models configurations using
        models_configure(): will take care of the inverse relations for
        foreignkeys and many2many
        '''

        DEFAULT_CONFIG.update(config)

        db_config = config.get('db_config', None)
        if not db_config:
            raise ModuleError('Imposible to configure without database configuration!')

        db_config['loop'] = self.loop = DEFAULT_CONFIG.get('loop')

        database_module = importlib.import_module('asyncorm.database')

        # we get the manager defined in the config file
        manager = getattr(database_module, DEFAULT_CONFIG['manager'])
        self.db_manager = manager(db_config)

        self._modules = [Module(m, self.db_manager) for m in config.pop('modules', []) or []]
        self._modules.append(Module('asyncorm.models.migrations', self.db_manager))
        # After the manager is set then we can build the rest of db features
        self._modules_models = {m.module_name: m.models for m in self._modules}

        self.models = {}
        for m in self._modules_models.values():
            self.models.update(m)

        self.models_configure()

    def get_model(self, model_name):
        if len(self.models) == 1:
            raise ModuleError('There are no modules declared in the orm')

        try:
            model_split = model_name.split('.')
            if len(model_split) == 2:
                return self._modules_models[model_split[0]][model_split[1]]
            elif len(model_split) == 1:
                return self.models[model_name]
            else:
                raise ModelError('The string declared should be in format "module.Model" or "Model"')
        except KeyError:
            raise ModuleError('The model does not exists')

    def models_configure(self):
        # and we set it to all the different models defined
        from asyncorm.models.fields import ForeignKey, ManyToManyField

        self.set_model_orm()

        for name, model in self.models.items():
            vvv = model.fields.values()
            for f in vvv:
                if isinstance(f, ManyToManyField):
                    m2m_tablename = '{}_{}'.format(name, f.foreign_key).lower()
                    other = self.get_model(f.foreign_key)
                    other.set_many2many(f, m2m_tablename, f.foreign_key, name)

                    model.set_many2many(f, m2m_tablename, name, f.foreign_key)

                elif isinstance(f, ForeignKey):
                    other_model = self.get_model(f.foreign_key)
                    other_model.set_reverse_foreignkey(name, f.db_column)

    def set_model_orm(self):
        for model in self.models.values():
            model.set_orm(self)

    async def create_db(self):
        """
        We  create all tables for each of the declared models
        """
        self.models_configure()
        for model in self.models.values():
            await model().objects.set_requirements()

        for model in self.models.values():
            await model().objects.create_table()

        for model in self.models.values():
            await model().objects.add_fk_columns()

        for model in self.models.values():
            await model().objects.add_m2m_columns()

        for model in self.models.values():
            await model().objects.add_table_indices()

        for model in self.models.values():
            await model().objects.unique_together()

    def sync_db(self):
        self.loop.run_until_complete(asyncio.gather(self.loop.create_task(self.create_db())))

    def make_migrations(self):
        for model in self.models.values():
            model().make_migration()


orm_app = OrmApp()


def parse_config(config_file):
    parsed_file = configparser.ConfigParser()

    parsed_file.read(config_file)

    # check all sections exist
    for section in ['db_config', 'orm']:
        if section not in parsed_file.sections():
            raise ConfigError('the file {} does not contain {} section!'.format(config_file, section))

    return {
        'db_config': {
            'database': parsed_file.get('db_config', 'database') or None,
            'host': parsed_file.get('db_config', 'host') or None,
            'user': parsed_file.get('db_config', 'user') or None,
            'password': parsed_file.get('db_config', 'password') or None,
        },
        'modules': parsed_file.get('orm', 'modules').split() or []
    }


def configure_orm(config=None, loop=None):
    # configure and return the already configured orm
    global orm_app

    if config is None:
        config = parse_config(os.path.join(os.getcwd(), DEFAULT_CONFIG_FILE))
    elif not isinstance(config, dict):
        config = parse_config(config)

    if loop is None:
        loop = asyncio.get_event_loop()

    config.update({'loop': loop})
    orm_app.configure(config)
    return orm_app


def get_model(model_name):
    # wrapper around the orm method
    return orm_app.get_model(model_name)
