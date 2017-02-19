from fields import Field, PkField, ManyToMany
from exceptions import ModelError


class Model(object):
    table_name = ''

    def __init__(self, **kwargs):
        # test done
        if not self.table_name:
            self.table_name = self.__class__.__name__.lower()
        self.fields, self.field_names = self.get_fields()
        self.validate(kwargs)

    def validate(self, kwargs):
        # test done
        attr_errors = [k for k in kwargs.keys() if k not in self.field_names]

        if attr_errors:
            err_string = '"{}" is not an attribute for {}'
            error_list = [
                err_string.format(k, self.__class__.__name__)
                for k in attr_errors
            ]
            raise ModelError(error_list)

        for k, v in kwargs.items():
            att_class = getattr(self.__class__, k).__class__
            att_class.validate(v)

    @property
    def fk_id(self):
        return [f for f in self.fields if isinstance(f, PkField)][0].field_name

    @classmethod
    def get_fields(cls):
        # test done
        fields = []
        field_names = []
        for f in cls.__dict__.keys():
            if isinstance(getattr(cls, f), Field):
                field = getattr(cls, f)

                if not field.field_name:
                    setattr(field, 'field_name', f)

                if isinstance(getattr(cls, f), ManyToMany):
                    setattr(
                        field,
                        'foreign_model',
                        cls.table_name or cls.__name__.lower()
                    )

                fields.append(field)
                field_names.append(f)

        if PkField not in [f.__class__ for f in fields]:
            fields = [PkField()] + fields
            field_names = ['id'] + field_names

        return fields, field_names

    def creation_query(self):
        return 'CREATE TABLE {table_name} ({field_queries});'.format(
            table_name=self.table_name,
            field_queries=self.get_field_queries(),
        )

    def get_field_queries(self):
        # builds the table with all its fields definition
        return ', '.join([f.creation_query() for f in self.fields
            if not isinstance(f, ManyToMany)])

    def get_m2m_field_queries(self):
        # builds the relational 1_to_1 table
        return '; '.join([f.creation_query() for f in self.fields
            if isinstance(f, ManyToMany)]
            )

    # async def save(self, fields):
    #     # performs the database save

    #     changes_stack = {}
    #     for f in self.field_names:
    #         field_data = getattr(self, f)
    #         if not isinstance(field_data, Field):
