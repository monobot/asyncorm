import json
import re

from decimal import Decimal
from uuid import UUID
from json.decoder import JSONDecodeError

from datetime import datetime, date, time
from ..exceptions import FieldError

DATE_FIELDS = ['DateField', ]

KWARGS_TYPES = {
    'auto_now': bool,
    'choices': (dict, tuple),
    'db_column': str,
    'db_index': bool,
    'decimal_places': int,
    'default': object,
    'foreign_key': str,
    'max_digits': int,
    'max_length': int,
    'null': bool,
    'reverse_field': str,
    'strftime': str,
    'unique': bool,
    'uuid_type': str,
}


class Field(object):
    internal_type = None
    creation_string = None
    required_kwargs = []
    table_name = None

    def __new__(mcs, **kwargs):
        if not getattr(mcs, 'internal_type'):
            raise NotImplementedError('Missing "internal_type" attribute from class definition')
        return super().__new__(mcs)

    def __init__(self, **kwargs):
        self.validate_kwargs(kwargs)
        self.field_type = self.__class__.__name__
        self.db_index = False

        for kw in kwargs.keys():
            setattr(self, kw, kwargs.get(kw))
            if kw == 'choices':
                if isinstance(kwargs.get(kw), dict):
                    self.choices = kwargs.get(kw)
                elif kwargs.get(kw) is None:
                    pass
                else:
                    self.choices = {k: v for k, v in kwargs.get(kw)}

    def creation_query(self):
        creation_string = '{db_column} ' + self.creation_string
        date_field = self.field_type in DATE_FIELDS

        if hasattr(self, 'default') and self.default is not None:
            creation_string += ' DEFAULT '
            default_value = self.default
            if callable(self.default):
                default_value = self.default()

            if isinstance(default_value, str):
                creation_string += '\'{}\''.format(default_value)
            elif isinstance(default_value, bool):
                creation_string += str(default_value)
            else:
                creation_string += '\'{}\''.format(self.sanitize_data(default_value))

        elif date_field and self.auto_now:
            creation_string += ' DEFAULT now()'

        creation_string += self.unique and ' UNIQUE' or ''
        creation_string += self.null and ' NULL' or ' NOT NULL'

        return creation_string.format(**self.__dict__)

    def validate_kwargs(self, kwargs):
        for kw in self.required_kwargs:
            if not kwargs.get(kw, None):
                raise FieldError('"{cls}" field requires {kw}'.format(cls=self.__class__.__name__, kw=kw))

        for k, v in kwargs.items():
            null_choices = v is None and k == 'choices'
            if not isinstance(v, KWARGS_TYPES[k]) and not null_choices:
                raise FieldError('Wrong value for {k}'.format(k=k))

        if kwargs.get('db_column', ''):
            self.set_field_name(kwargs['db_column'])

    def validate(self, value):
        if value is None and not self.null:
            raise FieldError('null value in NOT NULL field')

        if hasattr(self, 'choices') and self.choices is not None:
            if value not in self.choices.keys():
                raise FieldError('"{}" not in model choices'.format(value))

        if not isinstance(value, self.internal_type):
            raise FieldError(
                '{value} is a wrong datatype for field {cls}'.format(
                    value=value,
                    cls=self.__class__.__name__,
                )
            )

    @classmethod
    def recompose(cls, value):
        return value

    def sanitize_data(self, value):
        '''method used to convert to SQL data'''
        if value is None:
            return 'NULL'
        self.validate(value)
        return value

    def serialize_data(self, value):
        '''to directly serialize the data field pased'''
        return value

    def current_state(self):
        return {arg: getattr(self, arg) for arg in self.args}

    def set_field_name(self, db_column):
        if '__' in db_column:
            raise FieldError('db_column can not contain "__"')
        if db_column.startswith('_'):
            raise FieldError('db_column can not start with "_"')
        if db_column.endswith('_'):
            raise FieldError('db_column can not end with "_"')
        self.db_column = db_column


class BooleanField(Field):
    internal_type = bool
    creation_string = 'boolean'
    args = ('choices', 'db_column', 'db_index', 'default', 'null', 'unique', )

    def __init__(self, db_column='', default=None, null=False, unique=False, db_index=False):
        super().__init__(db_column=db_column, default=default, null=null, unique=unique, db_index=db_index)

    def sanitize_data(self, value):
        '''method used to convert to SQL data'''
        if value is None:
            return 'NULL'
        elif value is True:
            return 'true'
        elif value is False:
            return 'false'
        elif value in ['NULL', 'null', 'TRUE', 'true', 'FALSE', 'false']:
            return value
        raise FieldError('not correct data for BooleanField')


class CharField(Field):
    internal_type = str
    required_kwargs = ['max_length', ]
    creation_string = 'varchar({max_length})'
    args = ('choices', 'db_column', 'db_index', 'default', 'max_length', 'null', 'unique', )

    def __init__(
            self,
            db_column='', default=None, max_length=0, null=False, choices=None, unique=False,
            db_index=False):
        super().__init__(
            db_column=db_column,
            default=default,
            max_length=max_length,
            null=null,
            choices=choices,
            unique=unique,
            db_index=db_index,

        )

    @classmethod
    def recompose(cls, value):
        if value is not None:
            return value.replace('\;', ';').replace('\--', '--')
        return value

    def sanitize_data(self, value):
        value = super().sanitize_data(value)
        if len(value) > self.max_length:
            raise FieldError(
                'The string entered is bigger than the "max_length" defined ({})'.format(self.max_length))
        if value is not None:
            value = value.replace(';', '\;').replace('--', '\--')
        return '\'{}\''.format(value)


class EmailField(CharField):

    def validate(self, value):
        super(EmailField, self).validate(value)
        # now validate the emailfield here
        email_regex = r'^[\w][\w0-9_.+-]+@[\w0-9-]+\.[\w0-9-.]+$'
        if not re.match(email_regex, value):
            raise FieldError('"{}" not a valid email address'.format(value))


class TextField(Field):
    internal_type = str
    creation_string = 'text'
    args = ('choices', 'db_column', 'db_index', 'default', 'null', 'unique', )

    def __init__(
            self, db_column='', default=None, null=False, unique=False, db_index=False,
            choices=None):
        super().__init__(
                db_column=db_column, default=default, null=null, unique=unique, db_index=db_index,
                choices=choices)

    def sanitize_data(self, value):
        return "'{}'".format(super().sanitize_data(value))


# numeric fields
class NumberField(Field):
    pass


class IntegerField(NumberField):
    internal_type = int
    creation_string = 'integer'
    args = ('choices', 'db_column', 'db_index', 'default', 'null', 'unique', )

    def __init__(
            self, db_column='', default=None, null=False, choices=None, unique=False, db_index=False):
        super().__init__(
            db_column=db_column, default=default, null=null, choices=choices, unique=unique,
            db_index=db_index)

    def sanitize_data(self, value):
        return '{}'.format(super().sanitize_data(value))


class DecimalField(NumberField):
    internal_type = (Decimal, float, int)
    creation_string = 'decimal({max_digits},{decimal_places})'
    args = (
        'db_column', 'default', 'null', 'choices', 'unique', 'max_digits', 'decimal_places', 'db_index',
        )

    def __init__(
            self, db_column='', default=None, null=False, choices=None,
            unique=False, db_index=False,  max_digits=10, decimal_places=2):
        super().__init__(
            db_column=db_column, default=default, null=null, choices=choices, unique=unique,
            db_index=db_index,  max_digits=max_digits, decimal_places=decimal_places)

    def sanitize_data(self, value):
        return '{}'.format(super().sanitize_data(value))


# time fields
class AutoField(IntegerField):
    creation_string = 'serial PRIMARY KEY'
    args = ('choices', 'db_column', 'db_index', 'default', 'null', 'unique', )

    def __init__(self, db_column='id'):
        super().__init__(db_column=db_column, unique=True, null=False)


class DateTimeField(Field):
    internal_type = datetime
    creation_string = 'timestamp'
    strftime = '%Y-%m-%d  %H:%s'

    def sanitize_data(self, value):
        return "'{}'".format(super().sanitize_data(value))

    def serialize_data(self, value):
        return value.strftime(self.strftime)

    def __init__(
            self, db_column='', default=None, auto_now=False, null=False, choices=None,
            unique=False, db_index=False,  strftime=None):
        super().__init__(
            db_column=db_column, default=default, auto_now=auto_now, null=null, choices=choices,
            unique=unique, db_index=db_index,  strftime=strftime or self.strftime)


class DateField(DateTimeField):
    internal_type = date
    creation_string = 'date'
    args = (
        'auto_now', 'choices', 'db_column', 'db_index', 'default', 'null', 'strftime',
        'unique', )
    strftime = '%Y-%m-%d'


class TimeField(DateTimeField):
    internal_type = time
    creation_string = 'time'
    strftime = '%H:%s'


# relational fields
class ForeignKey(Field):
    internal_type = int
    required_kwargs = ['foreign_key', ]
    creation_string = 'integer references {foreign_key}'
    args = ('db_column', 'db_index', 'default', 'foreign_key', 'null', 'unique', )

    def __init__(self, db_column='', default=None, foreign_key='', null=False, unique=False, db_index=False):
        super().__init__(
            db_column=db_column, db_index=db_index, default=default, foreign_key=foreign_key, null=null,
            unique=unique)

    def sanitize_data(self, value):
        return str(super().sanitize_data(value))


class ManyToManyField(Field):
    internal_type = list, int
    required_kwargs = ['foreign_key', ]
    creation_string = '''
        {own_model} INTEGER REFERENCES {own_model} NOT NULL,
        {foreign_key} INTEGER REFERENCES {foreign_key} NOT NULL
    '''
    args = ('db_column', 'db_index', 'default', 'foreign_key', 'unique', )

    def __init__(self, db_column='', foreign_key=None, default=None, unique=False, db_index=False):
        super().__init__(
            db_column=db_column, foreign_key=foreign_key, default=default, unique=unique, db_index=db_index)

    def creation_query(self):
        return self.creation_string.format(**self.__dict__)

    def validate(self, value):
        if isinstance(value, list):
            for i in value:
                super().validate(i)
        else:
            super().validate(value)


# composite fields


class JsonField(Field):
    internal_type = dict, list, str
    required_kwargs = ['max_length', ]
    creation_string = 'varchar({max_length})'
    args = ('choices', 'db_column', 'db_index', 'default', 'max_length', 'null', 'unique', )

    def __init__(self,
            db_column='', default=None, max_length=0, null=False, choices=None, unique=False,
            db_index=False):
        super().__init__(
            db_column=db_column,
            default=default,
            max_length=max_length,
            null=null,
            choices=choices,
            unique=unique,
            db_index=db_index,
        )

    @classmethod
    def recompose(cls, value):
        return json.loads(value)

    def sanitize_data(self, value):
        self.validate(value)

        if value != 'NULL':
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except JSONDecodeError:
                    raise FieldError('The data entered can not be converted to json')
            value = json.dumps(value)

        if len(value) > self.max_length:
            raise FieldError(
                'The string entered is bigger than the "max_length" defined ({})'.format(self.max_length)
            )

        return '\'{}\''.format(value)


class Uuid4Field(Field):
    internal_type = UUID
    args = ('db_column', 'db_index', 'null', 'unique', 'uuid_type', )

    def __init__(
            self, db_column='', null=False, uuid_type='v4', db_index=False, unique=True):
        self.field_requirement = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'

        if uuid_type not in ['v1', 'v4']:
            raise FieldError('{} is not a recognized type'.format(uuid_type))

        super().__init__(
            db_column=db_column, unique=unique, db_index=db_index,
            default=None, null=null, uuid_type=uuid_type)

    @property
    def creation_string(self):
        uuid_types = {
            'v1': 'uuid_generate_v1mc',
            'v4': 'uuid_generate_v4',
        }
        return 'UUID DEFAULT {}()'.format(uuid_types[self.uuid_type])

    def sanitize_data(self, value):
        exp = r'^[a-zA-Z0-9\-\b]{36}$'
        if re.match(exp, value):
            return value
        raise FieldError('The expresion doesn\'t validate as a correct {}'.format(self.__class__.__name__))


class ArrayField(Field):
    internal_type = list
    creation_string = '{value_type} ARRAY'
    args = ('db_column', 'db_index', 'default', 'null', 'unique', 'value_type', )
    value_types = ('text', 'varchar', 'integer')

    def __init__(
            self, db_column='', default=None, null=True, unique=False, db_index=False, value_type='text'):
        super().__init__(db_column=db_column, default=default, unique=unique, db_index=db_index, null=null)
        self.value_type = value_type

    def sanitize_data(self, value):
        value = super().sanitize_data(value)
        if value:
            return 'ARRAY{}'.format(value)
        return 'ARRAY[]::{}[]'.format(self.value_type)

    def validate(self, value):
        super().validate(value)
        if value:
            items_type = self.homogeneous_type(value)
            if not items_type:
                raise FieldError('Array elements are not of the same type')
            if items_type == list:
                if not all(len(item) == len(value[0]) for item in value):
                    raise FieldError('Multi-dimensional arrays must have items of the same size')
        return value

    @staticmethod
    def homogeneous_type(value):
        iseq = iter(value)
        first_type = type(next(iseq))
        return first_type if all(isinstance(x, first_type) for x in iseq) else False
