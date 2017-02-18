from .exceptions import FieldError

__all__ = ('Field', 'PkField', 'CharField', 'IntegerField', 'DateField',
    'ForeignKey',
)

DATE_FIELDS = ['DateField', ]


class Field(object):

    def __init__(self, **kwargs):
        self.validate(kwargs)
        self.field_type = self.__class__.__name__

        self.field_name = kwargs.get('field_name', None)
        self.default = kwargs.get('default', None)
        self.null = kwargs.get('null', False)

        self.max_length = kwargs.get('max_length', None)
        self.foreign_key = kwargs.get('foreign_key', None)

        self.auto_now = kwargs.get('auto_now', False)

        self.kwargs = {
            'field_type': self.field_type,
            'field_name': self.field_name,
            'default': self.default,
            'null': self.null,
            'max_length': self.max_length,
            'foreign_key': self.foreign_key,
            'auto_now': self.auto_now,
        }

    def creation_query(self):
        # self.field_name = self.kwargs['field_name'] or field_name
        # self.kwargs['field_name'] = self.field_name

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

        return creation_string.format(**self.kwargs)

    def validate(self, kwargs):
        pass


class PkField(Field):

    def __init__(self, field_name='id'):
        self.creation_string = 'serial primary key'
        super().__init__(field_name=field_name)


class CharField(Field):

    def __init__(self, field_name=None, default=None, max_length=None,
            null=False):
        self.creation_string = 'varchar({max_length})'
        super().__init__(field_name=field_name, default=default,
            max_length=max_length, null=null
        )

    def validate(self, kwargs):
        if not kwargs.get('max_length', None):
            raise FieldError('"CharField" field requires max_length')


class IntegerField(Field):

    def __init__(self, field_name=None, default=None, null=False):
        self.creation_string = 'integer'
        super().__init__(field_name=field_name, default=default, null=null)


class DateField(Field):

    def __init__(self, field_name=None, default=None, auto_now=False,
            null=False):
        self.creation_string = 'timestamp'
        super().__init__(field_name=field_name, default=default,
            auto_now=auto_now, null=null
        )


class ForeignKey(Field):

    def __init__(self, field_name=None, foreign_key=None, default=None,
            null=False):
        self.creation_string = 'integer references {foreign_key}(id)'
        super().__init__(field_name=field_name, foreign_key=foreign_key,
            default=default, null=null
        )

    def validate(self, kwargs):
        if not kwargs.get('foreign_key', None):
            raise FieldError('"ForeignKey" field requires foreign_key')
