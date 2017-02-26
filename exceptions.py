__all__ = ('ModelError', 'FieldError', 'QuerysetError')


class ModelError(Exception):
    '''to be raised when there are model errors detected'''
    pass


class FieldError(Exception):
    '''to be raised when there are field errors detected'''
    pass


class QuerysetError(Exception):
    '''to be raised when there are queryset errors detected'''
    pass
