from .field import Field, PkField, ManyToMany


class Model(object):

    def __init__(self):
        self.table_name = self.__class__.__name__.lower()
        self.fields = self.get_fields()

    @property
    def fk_id(self):
        return [f for f in self.fields if isinstance(f, PkField)][0].field_name

    @classmethod
    def get_fields(cls):
        fields = [getattr(cls, f) for f in cls.__dict__.keys()
            if isinstance(getattr(cls, f), Field)
        ]
        if PkField not in [f.__class__ for f in fields]:
            fields = [PkField()] + fields

        return fields

    def creation_query(self):
        return 'CREATE TABLE {table_name} ({field_queries});'.format(
            table_name=self.table_name,
            field_queries=self.get_field_queries(),
        )

    def get_field_queries(self):
        return ', '.join([f.creation_query() for f in self.fields
            if not isinstance(f, ManyToMany)])
