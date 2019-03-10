from asyncorm.exceptions import AsyncOrmFieldError

DATE_FIELDS = ["DateField"]

KWARGS_TYPES = {
    "auto_now": bool,
    "choices": (dict, tuple),
    "db_column": str,
    "db_index": bool,
    "decimal_places": int,
    "default": object,
    "dialect": str,
    "foreign_key": str,
    "max_digits": int,
    "max_length": int,
    "null": bool,
    "protocol": str,
    "reverse_field": str,
    "strftime": str,
    "unpack_protocol": str,
    "unique": bool,
    "uuid_type": str,
}


class Field(object):
    """
    Base Field of AsyncOrm.

    Any developer defined Field should subclass Field.
    """

    internal_type = None
    creation_string = None
    required_kwargs = []
    table_name = None

    def __new__(cls, **kwargs):
        if cls.internal_type is None:
            raise NotImplementedError('Missing "internal_type" attribute from class definition')
        return super().__new__(cls)

    def __init__(self, **kwargs):
        self.validate_kwargs(kwargs)
        self.field_type = self.__class__.__name__
        self.db_index = False

        for kw in kwargs.keys():
            setattr(self, kw, kwargs.get(kw))
            if kw == "choices":
                if isinstance(kwargs.get(kw), dict):
                    self.choices = kwargs.get(kw)
                elif kwargs.get(kw) is None:
                    pass
                else:
                    self.choices = {k: v for k, v in kwargs.get(kw)}

    def creation_query(self):
        """Create the field's database creation query.

        :return: query constructed
        :rtype: str
        """
        creation_string = "{db_column} " + self.creation_string
        date_field = self.field_type in DATE_FIELDS

        if hasattr(self, "default") and self.default is not None:
            creation_string += " DEFAULT "
            default_value = self.default
            if callable(self.default):
                default_value = self.default()

            if isinstance(default_value, str):
                creation_string += "'{}'".format(default_value)
            elif isinstance(default_value, bool):
                creation_string += str(default_value)
            else:
                creation_string += "{}".format(self.sanitize_data(default_value))

        elif date_field and self.auto_now:
            creation_string += " DEFAULT now()"

        creation_string += self.unique and " UNIQUE" or ""
        creation_string += self.null and " NULL" or " NOT NULL"

        return creation_string.format(**self.__dict__)

    def validate_kwargs(self, kwargs):
        """Validate the kwargs provided.

        :param kwargs: Field creation kwargs
        :type kwargs: dict
        :raises AsyncOrmFieldError:
            If a required field is not provided or when a value
            provided doesn't comply to Field requirements.
        """
        for kw in self.required_kwargs:
            if not kwargs.get(kw, None):
                raise AsyncOrmFieldError('"{cls}" field requires {kw}'.format(cls=self.__class__.__name__, kw=kw))

        for k, v in kwargs.items():
            null_choices = v is None and k == "choices"
            if not isinstance(v, KWARGS_TYPES[k]) and not null_choices:
                raise AsyncOrmFieldError("Wrong value for {k}".format(k=k))

        if kwargs.get("db_column", ""):
            self.set_field_name(kwargs["db_column"])

    def validate(self, value):
        """Validate the value.

        :param value: value in the field
        :type value: self.internal_type
        :raises AsyncOrmFieldError:
            * When a null value sent to a non nullable field.
            * When the value provided is not in the field choices.
            * When the value provided is not in the self.internal_type
        """
        if value is None and not self.null:
            raise AsyncOrmFieldError("null value in NOT NULLABLE field")

        if hasattr(self, "choices") and self.choices is not None:
            if value not in self.choices.keys():
                raise AsyncOrmFieldError('"{}" not in field choices'.format(value))

        if value is not None and not isinstance(value, self.internal_type):
            raise AsyncOrmFieldError(
                "{value} is a wrong datatype for field {cls}".format(value=value, cls=self.__class__.__name__)
            )

    @classmethod
    def recompose(cls, value):
        return value

    def sanitize_data(self, value):
        """Sanitize the query before send to database."""
        self.validate(value)
        return value

    def serialize_data(self, value):
        """to directly serialize the data field passed"""
        return value

    def current_state(self):
        state = {"field_type": "{}.{}".format(self.__class__.__dict__["__module__"], self.__class__.__name__)}
        state.update({arg: getattr(self, arg) for arg in self.args})
        return state

    def set_field_name(self, db_column):
        if "__" in db_column:
            raise AsyncOrmFieldError('db_column can not contain "__"')
        if db_column.startswith("_"):
            raise AsyncOrmFieldError('db_column can not start with "_"')
        if db_column.endswith("_"):
            raise AsyncOrmFieldError('db_column can not end with "_"')
        self.db_column = db_column
