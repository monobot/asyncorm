import json
import re

from decimal import Decimal
from json.decoder import JSONDecodeError

from datetime import datetime
from ..exceptions import FieldError, ModuleError

DATE_FIELDS = ['DateField', ]

KWARGS_TYPES = {
    'db_column': str,
    'default': object,
    'null': bool,
    'max_length': int,
    'foreign_key': str,
    'auto_now': bool,
    'reverse_field': str,
    'choices': (dict, tuple),
    'unique': bool,
    'strftime': str,
    'max_digits': int,
    'decimal_places': int,
}


class Field(object):
    required_kwargs = []
    table_name = None

    def __init__(self, **kwargs):
        self.validate_kwargs(kwargs)
        self.field_type = self.__class__.__name__

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

        creation_string += self.null and ' NULL' or ' NOT NULL'

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
                creation_string += '\'{}\''.format(
                    self.sanitize_data(default_value)
                )

        elif date_field and self.auto_now:
            creation_string += ' DEFAULT now()'

        if self.unique:
            creation_string += ' UNIQUE'

        return creation_string.format(**self.__dict__)

    #######################################################
    #######################################################
    # def modificate_query(self):
    #     modificate_string = '{db_column} ' + self.modificate_string
    #     date_field = self.field_type in DATE_FIELDS

    #     modificate_string += self.null and ' NULL' or ' NOT NULL'

    #     if hasattr(self, 'default') and self.default is not None:
    #         modificate_string += ' DEFAULT '
    #         default_value = self.default
    #         if callable(self.default):
    #             default_value = self.default()

    #         if isinstance(default_value, str):
    #             modificate_string += '\'{}\''.format(default_value)
    #         elif isinstance(default_value, bool):
    #             modificate_string += str(default_value)
    #         else:
    #             modificate_string += '\'{}\''.format(
    #                 self.sanitize_data(default_value)
    #             )

    #     elif date_field and self.auto_now:
    #         modificate_string += ' DEFAULT now()'

    #     if self.unique:
    #         modificate_string += ' UNIQUE'

    #     return modificate_string.format(**self.__dict__)
    #######################################################
    #######################################################

    def validate_kwargs(self, kwargs):
        for kw in self.required_kwargs:
            if not kwargs.get(kw, None):
                raise FieldError(
                    '"{class_name}" field requires {kw}'.format(
                        class_name=self.__class__.__name__,
                        kw=kw,
                    )
                )

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
                '{} is a wrong datatype for field {}'.format(
                    value, self.__class__.__name__
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
        '''to directly serialize the data field based'''
        return value

    def current_state(self):
        return {arg: getattr(self, arg) for arg in self.args}

    # def make_migration(self, old_state):
    #     if old_state is None:
    #         return self.creation_query()

    #     current_state = self.current_state()

    #     if set(old_state.keys()) != set(current_state.keys()):
    #         raise ModuleError(
    #             'imposible to migrate, you should do that manually!'
    #         )

    #     difference = {}
    #     for key in self.args:

    #         if current_state[key] != old_state[key]:
    #             difference.update({key: current_state[key]})

    #     return difference or None

    def set_field_name(self, db_column):
        if '__' in db_column:
            raise FieldError('db_column can not contain "__"')
        if db_column.startswith('_'):
            raise FieldError('db_column can not start with "_"')
        if db_column.endswith('_'):
            raise FieldError('db_column can not end with "_"')
        self.db_column = db_column


class PkField(Field):
    internal_type = int
    creation_string = 'serial primary key'
    args = ('db_column', 'unique', 'null',)

    def __init__(self, db_column='id', null=False):
        super().__init__(db_column=db_column, unique=True, null=null)


class BooleanField(Field):
    internal_type = bool
    creation_string = 'boolean'
    args = ('db_column', 'default', 'null', 'unique', )

    def __init__(self, db_column='', default=None, null=False, unique=False):
        super().__init__(db_column=db_column, default=default,
                         null=null, unique=unique
                         )

    def sanitize_data(self, value):
        '''method used to convert to SQL data'''
        if value is None:
            return 'NULL'
        elif value is True:
            return 'true'
        elif value is False:
            return 'false'


class CharField(Field):
    internal_type = str
    required_kwargs = ['max_length', ]
    creation_string = 'varchar({max_length})'
    args = ('db_column', 'default', 'max_length', 'null', 'choices', 'unique')

    def __init__(self, db_column='', default=None, max_length=0,
                 null=False, choices=None, unique=False
                 ):
        super().__init__(db_column=db_column, default=default,
                         max_length=max_length, null=null, choices=choices,
                         unique=unique
                         )

    def sanitize_data(self, value):
        value = super().sanitize_data(value)
        if len(value) > self.max_length:
            raise FieldError(
                ('The string entered is bigger than '
                 'the "max_length" defined ({})'
                 ).format(self.max_length)
            )
        return '\'{}\''.format(value)


class EmailField(CharField):

    def validate(self, value):
        super(EmailField, self).validate(value)
        # now validate the emailfield here
        email_regex = r'(^[\w][\w0-9_.+-]+@[\w0-9-]+\.[\w0-9-.]+$)'
        if not re.match(email_regex, value):
            raise FieldError('"{}" not a valid email address'.format(value))


class JsonField(Field):
    internal_type = dict, list, str
    required_kwargs = ['max_length', ]
    creation_string = 'varchar({max_length})'
    args = ('db_column', 'default', 'max_length', 'null', 'choices', 'unique')

    def __init__(self, db_column='', default=None, max_length=0,
                 null=False, choices=None, unique=False
                 ):
        super().__init__(
            db_column=db_column, default=default,
            max_length=max_length, null=null, choices=choices,
            unique=unique
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
                    raise FieldError(
                        'The data entered can not be converted to json'
                    )
            value = json.dumps(value)

        if len(value) > self.max_length:
            raise FieldError(
                ('The string entered is bigger than '
                 'the "max_length" defined ({})'
                 ).format(self.max_length)
            )

        return '\'{}\''.format(value)


class NumberField(Field):
    pass


class IntegerField(NumberField):
    internal_type = int
    creation_string = 'integer'
    args = ('db_column', 'default', 'null', 'choices', 'unique')

    def __init__(self, db_column='', default=None, null=False, choices=None,
                 unique=False):
        super().__init__(db_column=db_column, default=default, null=null,
                         choices=choices, unique=unique)

    def sanitize_data(self, value):
        value = super().sanitize_data(value)

        return '{}'.format(value)


class DecimalField(NumberField):
    internal_type = (Decimal, float, int)
    creation_string = 'decimal({max_digits},{decimal_places})'
    args = ('db_column', 'default', 'null', 'choices', 'unique',
            'max_digits', 'decimal_places')

    def __init__(self, db_column='', default=None, null=False, choices=None,
                 unique=False, max_digits=10, decimal_places=2):
        super().__init__(db_column=db_column, default=default, null=null,
                         choices=choices, unique=unique,
                         max_digits=max_digits, decimal_places=decimal_places)

    def sanitize_data(self, value):
        value = super().sanitize_data(value)

        return '{}'.format(value)


class DateField(Field):
    internal_type = datetime
    creation_string = 'timestamp'
    args = ('db_column', 'default', 'auto_now', 'null', 'choices', 'unique',
            'strftime')

    def __init__(self, db_column='', default=None, auto_now=False, null=False,
                 choices=None, unique=False, strftime='date %Y-%m-%d'
                 ):
        super().__init__(db_column=db_column, default=default,
                         auto_now=auto_now, null=null, choices=choices,
                         unique=unique, strftime=strftime
                         )

    def sanitize_data(self, value):
        value = super().sanitize_data(value)

        return "'{}'".format(value)

    def serialize_data(self, value):
        return value.strftime(self.strftime)


class ForeignKey(Field):
    internal_type = int
    required_kwargs = ['foreign_key', ]
    creation_string = 'integer references {foreign_key}'
    args = ('db_column', 'default', 'foreign_key', 'null', 'unique')

    def __init__(self, db_column='', default=None, foreign_key='',
                 null=False, unique=False):
        super().__init__(db_column=db_column, default=default,
                         foreign_key=foreign_key, null=null, unique=unique
                         )

    def sanitize_data(self, value):
        value = super().sanitize_data(value)
        return str(value)


class ManyToManyField(Field):
    internal_type = list, int
    required_kwargs = ['foreign_key', ]
    creation_string = '''
        {own_model} INTEGER REFERENCES {own_model} NOT NULL,
        {foreign_key} INTEGER REFERENCES {foreign_key} NOT NULL
    '''
    args = ('db_column', 'default', 'foreign_key', 'unique')

    def __init__(self, db_column='', foreign_key=None, default=None,
                 unique=False):
        super().__init__(db_column=db_column, foreign_key=foreign_key,
                         default=default, unique=unique
                         )

    def creation_query(self):
        return self.creation_string.format(**self.__dict__)

    def validate(self, value):
        if isinstance(value, list):
            for i in value:
                super().validate(i)
        else:
            super().validate(value)
