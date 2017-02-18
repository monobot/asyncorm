from .exceptions import FieldError
from .field import Field


class Model(object):

    def __init__(self):
        self.table_name = self.__class__.__name__.lower()
        self.get_fields()

    def get_fields(self):
        self.fields = [f for f in self.__dict__.keys() if isinstance(f, Field)]

    def creation_query(self):
        return 'CREATE TABLE {table_name} ({field_queries});'.format(
            table_name=self.table_name,
            field_queries=self.get_field_queries(),
        )

    def get_field_queries(self):
        return ', '.join([field.creation_query() for field in self.fields])
