from exceptions import FieldError

__all__ = ('Field', 'PkField', 'CharField', 'IntegerField', 'DateField',
    'ForeignKey',
)

DATE_FIELDS = ['DateField', ]


class Field(object):

    def __init__(self, **kwargs):
        self.validate_kwargs(kwargs)
        self.field_type = self.__class__.__name__

        self.field_name = kwargs.get('field_name', None)
        self.default = kwargs.get('default', None)
        self.null = kwargs.get('null', False)

        self.max_length = kwargs.get('max_length', None)
        self.foreign_key = kwargs.get('foreign_key', None)

        self.auto_now = kwargs.get('auto_now', False)
        self.reverse_field = kwargs.get('reverse_field', None)

    def creation_query(self):
        creation_string = '{field_name} ' + self.creation_string
        date_field = self.field_type in DATE_FIELDS

        creation_string += self.null and ' NULL' or ' NOT NULL'

        default_value = self.default
        if default_value:
            creation_string += ' DEFAULT \'{default}\''
            if callable(self.default):
                default_value = default_value()
                self.default = default_value
        elif date_field and self.auto_now:
            creation_string += ' DEFAULT now()'

        return creation_string.format(**self.__dict__)

    def validate_kwargs(self, kwargs):
        pass


class PkField(Field):

    def __init__(self, field_name='id'):
        self.creation_string = 'serial primary key'
        super().__init__(field_name=field_name)

    @classmethod
    def validate(cls, value):
        if not isinstance(value, int):
            raise FieldError(
                '{} is a wrong datatype for field {}'.format(
                    value,
                    cls.__name__
                )
            )


class CharField(Field):

    def __init__(self, field_name=None, default=None, max_length=None,
            null=False):
        self.creation_string = 'varchar({max_length})'
        super().__init__(field_name=field_name, default=default,
            max_length=max_length, null=null
        )

    def validate_kwargs(self, kwargs):
        if not kwargs.get('max_length', None):
            raise FieldError('"CharField" field requires max_length')

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise FieldError(
                '{} is a wrong datatype for field {}'.format(
                    value,
                    cls.__name__
                )
            )


class IntegerField(Field):

    def __init__(self, field_name=None, default=None, null=False):
        self.creation_string = 'integer'
        super().__init__(field_name=field_name, default=default, null=null)

    @classmethod
    def validate(cls, value):
        if not isinstance(value, int):
            raise FieldError(
                '{} is a wrong datatype for field {}'.format(
                    value,
                    cls.__name__
                )
            )


class DateField(Field):

    def __init__(self, field_name=None, default=None, auto_now=False,
            null=False):
        self.creation_string = 'timestamp'
        super().__init__(field_name=field_name, default=default,
            auto_now=auto_now, null=null
        )

    @classmethod
    def validate(cls, value):
        from datetime import datetime
        if not isinstance(value, datetime):
            raise FieldError(
                '{} is a wrong datatype for field {}'.format(
                    value,
                    cls.__name__
                )
            )


class ForeignKey(Field):

    def __init__(self, field_name=None, default=None, foreign_key=None,
            null=False):
        self.creation_string = 'integer references {foreign_key}'
        super().__init__(field_name=field_name, default=default,
            foreign_key=foreign_key, null=null
        )

    def validate_kwargs(self, kwargs):
        if not kwargs.get('foreign_key', None):
            raise FieldError('"ForeignKey" field requires foreign_key')

    @classmethod
    def validate(cls, value):
        if not isinstance(value, int):
            raise FieldError(
                '{} is a wrong datatype for field {}'.format(
                    value,
                    cls.__name__
                )
            )


class ManyToMany(Field):

    def __init__(self, field_name=None, foreign_key=None, default=None):
        self.creation_string = '''
            CREATE TABLE {foreign_model}_{foreign_key} (
            {foreign_model} INTEGER REFERENCES {foreign_model} NOT NULL,
            {foreign_key} INTEGER REFERENCES {foreign_key} NOT NULL
            );'''
        super().__init__(field_name=field_name, foreign_key=foreign_key,
            default=default
        )

    def creation_query(self):
        return self.creation_string.format(**self.__dict__)

    def validate_kwargs(self, kwargs):
        if not kwargs.get('foreign_key', None):
            raise FieldError('"ManyToMany" field requires foreign_key')

    @classmethod
    def validate(cls, value):
        if isinstance(value, list):
            for i in value:
                if not isinstance(i, int):
                    raise FieldError(
                        '{} is a wrong datatype for field {}'.format(
                            value,
                            cls.__name__
                        )
                    )
            return
        if not isinstance(value, int):
            raise FieldError(
                '{} is a wrong datatype for field {}'.format(
                    value,
                    cls.__name__
                )
            )
