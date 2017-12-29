import inspect
import importlib
import logging

logger = logging.getLogger('asyncorm')


class Module(object):
    def __init__(self, relative_name):
        self.name = relative_name
        self.module_name = relative_name.split('.')[-1]
        self.models = self.get_declared_models()

    def get_declared_models(self):
        # this import should be here otherwise causes circular import
        from asyncorm import models

        _models = {}
        try:
            module = importlib.import_module('{}.models'.format(self.name))
        except ImportError:
            logger.error('unable to import {}'.format(self.module_name))

        for k, v in inspect.getmembers(module):
            try:
                if issubclass(v, models.Model) and v is not models.Model:
                    _models[k] = v
                    _models.update({k: v})
            except TypeError:
                pass
        return _models
