import asyncio
import configparser
import importlib
import inspect
import logging
import os

from asyncorm.apps.app import App
from asyncorm.apps.app_config import AppConfig
from asyncorm.exceptions import ConfigError, AppError, ModelError

logger = logging.getLogger("asyncorm")


DEFAULT_CONFIG_FILE = "asyncorm.ini"


class OrmApp(object):
    _conf = {
        "db_config": None,
        "loop": asyncio.get_event_loop(),
        "manager": "PostgresManager",
        "apps": None,
    }

    def configure(self, config):
        """
        Configures the system:
        get all the models declared
        sets the database configured and adds the loop

        Then the database manager is configured, and set to all the
        models previously declared
        and then we finish the models configurations using
        models_configure(): will take care of the inverse relations for foreignkeys and many2many
        """

        self._conf.update(config)

        db_config = config.get("db_config", None)
        if not db_config:
            raise AppError("Imposible to configure without database configuration!")

        db_config["loop"] = self.loop = self._conf.get("loop")

        database_module = importlib.import_module("asyncorm.database")

        # we get the manager defined in the config file
        manager = getattr(database_module, self._conf["manager"])
        self.db_manager = manager(db_config)

        app_names = self._conf.pop("apps", []) or []
        self.apps = self._get_declared_apps(app_names)

        self.models = {}
        for module in self.apps.values():
            self.models.update(module.models)

        self.models_configure()

    def _get_declared_apps(self, app_names):
        _apps = {}
        app_names.append("asyncorm.migrations")
        for app_name in app_names:
            # its not required to include .app when the app is declared in that specific file_name
            import_str = not app_name.endswith(".app") and app_name + ".app" or app_name
            try:
                module = importlib.import_module(import_str)
            except ImportError:
                try:
                    import_str = ".".join(import_str.split(".")[:-1])
                    module = importlib.import_module(import_str)
                except ImportError:
                    logger.error("unable to import {}".format(import_str))
            for k, v in inspect.getmembers(module):
                try:
                    if issubclass(v, AppConfig) and v is not AppConfig:
                        # the instance directory is the import_str without the app.py file_name
                        dir_name = ".".join(import_str.split(".")[:-1])
                        abs_path = os.sep.join(module.__file__.split(os.sep)[:-1])

                        app = App(v.name, dir_name, abs_path, self)
                        _apps.update({v.name: app})
                except TypeError:
                    logger.debug("typerror")
        return _apps

    def get_model(self, model_name):
        if len(self.models) == 1:
            raise AppError("There are no apps declared in the orm")

        try:
            model_split = model_name.split(".")
            if len(model_split) == 2:
                return self.apps[model_split[0]].models[model_split[1]]
            elif len(model_split) == 1:
                return self.models[model_name]
            else:
                raise ModelError(
                    'The string declared should be in format "module.Model" or "Model"'
                )
        except KeyError:
            raise AppError("The model does not exists")

    def models_configure(self):
        # and we set it to all the different models defined
        from asyncorm.models.fields import ForeignKey, ManyToManyField

        self.set_model_orm()

        for name, model in self.models.items():
            vvv = model.fields.values()
            for f in vvv:
                if isinstance(f, ManyToManyField):
                    m2m_tablename = "{}_{}".format(name, f.foreign_key).lower()
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
        self.loop.run_until_complete(
            asyncio.gather(self.loop.create_task(self.create_db()))
        )


orm_app = OrmApp()


def parse_config(config_file):
    parsed_file = configparser.ConfigParser()

    parsed_file.read(config_file)

    # check all sections exist
    for section in ["db_config", "orm"]:
        if section not in parsed_file.sections():
            raise ConfigError(
                "the file {} does not contain {} section!".format(config_file, section)
            )

    return {
        "db_config": {
            "database": parsed_file.get("db_config", "database") or None,
            "host": parsed_file.get("db_config", "host") or None,
            "port": parsed_file.get("db_config", "port") or None,
            "user": parsed_file.get("db_config", "user") or None,
            "password": parsed_file.get("db_config", "password") or None,
        },
        "apps": parsed_file.get("orm", "apps").split() or [],
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

    config.update({"loop": loop})
    orm_app.configure(config)
    return orm_app


def get_model(model_name):
    # wrapper around the orm method
    return orm_app.get_model(model_name)
