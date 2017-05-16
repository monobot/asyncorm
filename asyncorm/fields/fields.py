import json

from datetime import datetime

from ..exceptions import FieldError  # , ModuleError

DATE_FIELDS = ['DateField', ]

KWARGS_TYPES = {
    'field_name': str,
    'default': object,
    'null': bool,
    'max_length': int,
    'foreign_key': str,
    'auto_now': bool,
    'reverse_field': str,
    'choices': (dict, tuple),
    'unique': bool,
    'strftime': str,
}


class Field(object):
    required_kwargs = []
    table_name = None

    def __init__(self, **kwargs):
        self._validate_kwargs(kwargs)
        self.field_type = self.__class__.__name__

        for kw in kwargs.keys():
            setattr(self, kw, kwargs.get(kw))
            if kw == 'choices':
                self.choices = {k: v for k, v in kwargs.get(kw)}

    def _creation_query(self):
        creation_string = '{field_name} ' + self.creation_string
        date_field = self.field_type in DATE_FIELDS

        creation_string += self.null and ' NULL' or ' NOT NULL'

        default_value = ''
        if hasattr(self, 'default'):
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

        if self.unique:
            creation_string += ' UNIQUE'

        return creation_string.format(**self.__dict__)

    def _field_constraints(self):
        if self.choices:
            key_list = ['\'{}\''.format(k) for k in self.choices.keys()]

            return_query = '''
                ALTER TABLE {table_name}
                ADD CONSTRAINT {const_name}
                CHECK ({field_name} IN ({key_list}) );
            '''
            return return_query.format(
                table_name=self.table_name,
                const_name='{}_{}_const'.format(
                    self.table_name,
                    self.field_name
                ),
                field_name=self.field_name,
                key_list=','.join(key_list),
            )
        return ''

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

    def _validate(self, value):
        if not value and not self.null:
            raise FieldError('null value in NOT NULL field')
        if not isinstance(value, self.internal_type):
            raise FieldError(
                '{} is a wrong datatype for field {}'.format(
                    value, self.__class__.__name__
                )
            )

    @classmethod
    def _recompose(cls, value):
        return value

    def _sanitize_data(self, value):
        '''method used to convert to SQL data'''
        if value is None:
            return 'NULL'
        self._validate(value)
        return value

    def _serialize_data(self, value):
        '''to directly serialize the data field based'''
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
    internal_type = object
    creation_string = 'serial primary key'

    def __init__(self, field_name='id', unique=False, null=False):
        super().__init__(field_name=field_name, unique=unique, null=null)


class CharField(Field):
    internal_type = str
    required_kwargs = ['max_length', ]
    creation_string = 'varchar({max_length})'

    def __init__(self, field_name='', default=None, max_length=0,
                 null=False, choices={}, unique=False
                 ):
        super().__init__(field_name=field_name, default=default,
                         max_length=max_length, null=null, choices=choices,
                         unique=unique
                         )

    def _sanitize_data(self, value):
        value = super()._sanitize_data(value)
        if len(value) > self.max_length:
            raise FieldError(
                ('The string entered is bigger than '
                 'the "max_length" defined ({})'
                 ).format(self.max_length)
            )
        return '\'{}\''.format(value)


class JsonField(CharField):
    internal_type = dict, list, str

    def __init__(self, field_name='', default=None, max_length=0,
                 null=False, choices={}, unique=False
                 ):
        super().__init__(field_name=field_name, default=default,
                         max_length=max_length, null=null, choices=choices,
                         unique=unique
                         )

    @classmethod
    def _recompose(cls, value):
        return json.loads(value)

    def _sanitize_data(self, value):
        if value is None:
            return 'NULL'
        self._validate(value)

        if value != 'NULL':
            try:
                value = json.dumps(value)

            except SyntaxError:
                raise FieldError(
                    'The data entered can not be converted to json'
                )
        if len(value) > self.max_length:
            raise FieldError(
                ('The string entered is bigger than '
                 'the "max_length" defined ({})'
                 ).format(self.max_length)
            )
        return '\'{}\''.format(value)


class IntegerField(Field):
    internal_type = int
    creation_string = 'integer'

    def __init__(self, field_name='', default=None, null=False, choices={},
                 unique=False):
        super().__init__(field_name=field_name, default=default, null=null,
                         choices=choices, unique=unique)

    def _sanitize_data(self, value):
        value = super()._sanitize_data(value)

        return '{}'.format(value)


class DecimalField(IntegerField):
    internal_type = float
    creation_string = 'decimal'


class DateField(Field):
    internal_type = datetime
    creation_string = 'timestamp'

    def __init__(self, field_name='', default=None, auto_now=False, null=False,
                 choices={}, unique=False, strftime='date %Y-%m-%d'
                 ):
        super().__init__(field_name=field_name, default=default,
                         auto_now=auto_now, null=null, choices=choices,
                         unique=unique, strftime=strftime
                         )

    def _sanitize_data(self, value):
        value = super()._sanitize_data(value)

        return "'{}'".format(value)

    def _serialize_data(self, value):
        return value.strftime(self.strftime)


class ForeignKey(Field):
    internal_type = int
    required_kwargs = ['foreign_key', ]
    creation_string = 'integer references {foreign_key}'

    def __init__(self, field_name='', default=None, foreign_key='',
                 null=False, unique=False):
        super().__init__(field_name=field_name, default=default,
                         foreign_key=foreign_key, null=null, unique=unique
                         )

    def _sanitize_data(self, value):
        value = super()._sanitize_data(value)
        return str(value)


class ManyToMany(Field):
    internal_type = list, int
    required_kwargs = ['foreign_key', ]
    creation_string = '''
        {own_model} INTEGER REFERENCES {own_model} NOT NULL,
        {foreign_key} INTEGER REFERENCES {foreign_key} NOT NULL
    '''

    def __init__(self, field_name='', foreign_key=None, default=None,
                 unique=False):
        super().__init__(field_name=field_name, foreign_key=foreign_key,
                         default=default, unique=unique
                         )

    def _creation_query(self):
        return self.creation_string.format(**self.__dict__)

    def _validate(self, value):
        if isinstance(value, list):
            for i in value:
                super()._validate(i)
        else:
            super()._validate(value)
