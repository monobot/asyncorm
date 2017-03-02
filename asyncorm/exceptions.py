__all__ = ('ModuleError', 'ModelError', 'FieldError', 'QuerysetError')


class ModuleError(Exception):
    '''to be raised when there are model module or config errors detected'''
    pass


class ModelError(Exception):
    '''to be raised when there are model errors detected'''
    pass


class FieldError(Exception):
    '''to be raised when there are field errors detected'''
    pass


class QuerysetError(Exception):
    '''to be raised when there are queryset errors detected'''
    pass
