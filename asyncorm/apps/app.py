import importlib
import inspect
import logging

from asyncorm.apps.app_migration import AppMigration

logger = logging.getLogger("asyncorm")


class App(AppMigration):
    """An App (application) describes a set of features for your
    development, all the kind of objects that related together should
    be defined in the same Application.
    """

    def __init__(self, name, relative_name, abs_path, orm):
        """The Apps are constructed via introspection by asyncOrm, you
        should only have to set the entry point of the app by setting
        the AppConfig.

        :param name: the name of the app.
        :type name: string
        :param relative_name: This is the relative path to the app from
        the source code of the whole program.
        :type relative_name: string
        :param abs_path: This is the absolute path of the app.
        :type abs_path: string
        :param orm: The ORM singleton been handled to the App
        constructor.
        :type orm: OrmApp
        """
        self.relative_name = relative_name
        self.abs_path = abs_path
        self.name = name
        self.orm = orm
        self.db_backend = orm.db_backend
        self.models = self.get_declared_models()

    def get_declared_models(self):
        """Constructs the declared models in the App via introspection.

        :return: list of models for an specific App
        :rtype: list(asyncorm.models.Model)
        """
        # this import should be here otherwise causes circular import
        from asyncorm import models

        _models = {}
        try:
            module = importlib.import_module("{}.models".format(self.relative_name))
        except ImportError:
            logger.exception("unable to import %s", self.relative_name)

        for k, v in inspect.getmembers(module):
            try:
                if issubclass(v, models.Model) and v is not models.Model:
                    v.orm_app = self
                    _models.update({k: v})
            except TypeError:
                pass
        return _models
