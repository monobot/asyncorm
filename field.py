from .exceptions import FieldError

__all__ = ('PkField', 'CharField', 'IntegerField', 'DateField')

DATE_FIELDS = ['DateField', ]


class Field(object):

    def __init__(self, field_name, **kwargs):
        self.validate(kwargs)
        self.field_type = self.__class__.__name__
        self.field_name = field_name
        self.kwargs = kwargs
        self.kwargs.update({'field_name': field_name})

    def creation_query(self):
        creation_string = self.field_creation_string
        date_field = self.field_type in DATE_FIELDS
        if self.kwargs.get('default', False):
            creation_string += ' DEFAULT \'{default}\''
        elif date_field and self.kwargs.get('auto_now', False):
            creation_string += ' DEFAULT now()'

        return creation_string.format(**self.kwargs)

    def validate(self, kwargs):
        pass


class PkField(Field):

    def __init__(self, field_name='id'):
        super().__init__(field_name=field_name)

    @property
    def field_creation_string(self):
        return '{field_name} serial primary key'


class CharField(Field):

    def __init__(self, field_name, default=None, max_length=None):
        super().__init__(field_name, default=default, max_length=max_length)

    def validate(self, kwargs):
        if not kwargs.get('max_length', None):
            raise FieldError('"CharField" field requires max_length')

    @property
    def field_creation_string(self):
        return '{field_name} varchar({max_length})'


class IntegerField(Field):

    @property
    def field_creation_string(self):
        return '{field_name} integer'


class DateField(Field):

    def __init__(self, field_name, default=None, auto_now=False):
        super().__init__(field_name, default=default, auto_now=auto_now)

    @property
    def field_creation_string(self):
        return '{field_name} timestamp'
