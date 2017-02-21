from exceptions import FieldError
from datetime import datetime

__all__ = ('Field', 'PkField', 'CharField', 'IntegerField', 'DateField',
    'ForeignKey', 'ManyToMany', 'DecimalField'
)

DATE_FIELDS = ['DateField', ]

KWARGS_TYPES = {
    'field_name': str,
    'default': object,
    'null': bool,
    'max_length': int,
    'foreign_key': str,
    'auto_now': bool,
    'reverse_field': str,
}


class Field(object):
    required_kwargs = []

    def __init__(self, **kwargs):
        self._validate_kwargs(kwargs)
        self.field_type = self.__class__.__name__

        self.field_name = kwargs.get('field_name', '')

        self.default = kwargs.get('default', None)
        self.null = kwargs.get('null', False)

        self.max_length = kwargs.get('max_length', 0)

        self.foreign_key = kwargs.get('foreign_key', '')

        self.auto_now = kwargs.get('auto_now', False)
        self.reverse_field = kwargs.get('reverse_field', '')

    def _creation_query(self):
        creation_string = '{field_name} ' + self.creation_string
        date_field = self.field_type in DATE_FIELDS

        creation_string += self.null and ' NULL' or ' NOT NULL'

        default_value = self.default
        if default_value:
            creation_string += ' DEFAULT '
            if callable(self.default):
                default_value = default_value()
                self.default = default_value

            if isinstance(default_value, str):
                creation_string += '\'{}\''.format(default_value)
            else:
                creation_string += default_value

        elif date_field and self.auto_now:
            creation_string += ' DEFAULT now()'

        return creation_string.format(**self.__dict__)

    def _validate_kwargs(self, kwargs):
        for kw in self.required_kwargs:
            if not kwargs.get(kw, None):
                raise FieldError(
                    '"{class_name}" field requires {kw}'.format(
                        class_name=self.__class__.__name__,
                        kw=kw,
                    )
                )

        for k, v in kwargs.items():
            check = isinstance(v, KWARGS_TYPES[k])
            if not check:
                raise FieldError('Wrong value for {k}'.format(k=k))

        if kwargs.get('field_name', ''):
            self._set_field_name(kwargs['field_name'])

    @classmethod
    def _validate(cls, value):
        if not isinstance(value, cls.internal_type):
            raise FieldError(
                '{} is a wrong datatype for field {}'.format(
                    value, cls.__name__
                )
            )

    def _sanitize_data(self, value):
        self._validate(value)
        return value

    def _set_field_name(self, field_name):
        if '__' in field_name:
            raise FieldError('field_name can not contain "__"')
        if field_name.startswith('_'):
            raise FieldError('field_name can not start with "_"')
        if field_name.endswith('_'):
            raise FieldError('field_name can not end with "_"')
        self.field_name = field_name


class PkField(Field):

    def __init__(self, field_name='id'):
        self.creation_string = 'serial primary key'
        super().__init__(field_name=field_name)

    @classmethod
    def _validate(cls, value):
        raise FieldError('Models can not be generated with forced id')


class CharField(Field):
    internal_type = str
    required_kwargs = ['max_length', ]

    def __init__(self, field_name='', default=None, max_length=0,
            null=False):
        self.creation_string = 'varchar({max_length})'
        super().__init__(field_name=field_name, default=default,
            max_length=max_length, null=null
        )

    def _sanitize_data(self, value):
        super()._sanitize_data(value)

        if len(value) > self.max_length:
            raise FieldError(
                ('The string entered is bigger than '
                    'the "max_length" defined ({})'
                ).format(self.max_length)
            )
        return "'{}'".format(value)


class IntegerField(Field):
    internal_type = int

    def __init__(self, field_name='', default=None, null=False):
        self.creation_string = 'integer'
        super().__init__(field_name=field_name, default=default, null=null)


class DecimalField(Field):
    internal_type = float

    def __init__(self, field_name='', default=None, null=False):
        self.creation_string = 'integer'
        super().__init__(field_name=field_name, default=default, null=null)


class DateField(Field):
    internal_type = datetime

    def __init__(self, field_name='', default=None, auto_now=False,
            null=False):
        self.creation_string = 'timestamp'
        super().__init__(field_name=field_name, default=default,
            auto_now=auto_now, null=null
        )

    def _sanitize_data(self, value):
        super()._sanitize_data(value)

        return "'{}'".format(value)


class ForeignKey(Field):
    internal_type = int
    required_kwargs = ['foreign_key', ]

    def __init__(self, field_name='', default=None, foreign_key='',
            null=False):
        self.creation_string = 'integer references {foreign_key}'
        super().__init__(field_name=field_name, default=default,
            foreign_key=foreign_key, null=null
        )


class ManyToMany(Field):
    internal_type = int
    required_kwargs = ['foreign_key', ]

    def __init__(self, field_name='', foreign_key='', default=None):
        self.creation_string = '''
            CREATE TABLE {table_name} (
            {foreign_model} INTEGER REFERENCES {foreign_model} NOT NULL,
            {foreign_key} INTEGER REFERENCES {foreign_key} NOT NULL
            );'''
        super().__init__(field_name=field_name, foreign_key=foreign_key,
            default=default
        )

    def _creation_query(self):
        return self.creation_string.format(**self.__dict__)

    @classmethod
    def _validate(cls, value):
        if isinstance(value, list):
            for i in value:
                super()._validate(value)
            return
        super()._validate(value)
