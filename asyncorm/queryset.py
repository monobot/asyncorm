__all__ = ['Queryset', ]

MIDDLE_OPERATOR = {
    'gt': '>',
    'lt': '<',
    'gte': '>=',
    'lte': '<=',
}


class Queryset(object):

    def __init__(self, model, query):
        self.model = model
        self.query = query
