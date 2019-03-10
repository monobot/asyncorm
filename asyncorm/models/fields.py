import json
import re
from datetime import date, datetime, time
from decimal import Decimal
from json.decoder import JSONDecodeError
from uuid import UUID

from netaddr import EUI, IPNetwork, mac_bare, mac_cisco, mac_eui48, mac_pgsql, mac_unix, mac_unix_expanded
from netaddr.core import AddrFormatError

from asyncorm.exceptions import AsyncOrmFieldError
from asyncorm.models.field import Field

DATE_FIELDS = ["DateField"]


class BooleanField(Field):
    internal_type = bool
    creation_string = "boolean"
    args = ("choices", "db_column", "db_index", "default", "null", "unique")

    def __init__(self, db_column="", db_index=False, default=None, null=False, unique=False):
        super().__init__(db_column=db_column, db_index=db_index, default=default, null=null, unique=unique)

    def sanitize_data(self, value):
        """method used to convert to SQL data"""
        if isinstance(value, bool) or value is None:
            return value
        raise AsyncOrmFieldError("not correct data for BooleanField")


class CharField(Field):
    internal_type = str
    required_kwargs = ["max_length"]
    creation_string = "varchar({max_length})"
    args = ("choices", "db_column", "db_index", "default", "max_length", "null", "unique")

    def __init__(
        self, choices=None, db_column="", db_index=False, default=None, max_length=0, null=False, unique=False
    ):
        super().__init__(
            choices=choices,
            db_column=db_column,
            db_index=db_index,
            default=default,
            max_length=max_length,
            null=null,
            unique=unique,
        )

    @classmethod
    def recompose(cls, value):
        if value is not None:
            return value.replace("\;", ";").replace("\--", "--")
        return value

    def sanitize_data(self, value):
        value = super().sanitize_data(value)
        if len(value) > self.max_length:
            raise AsyncOrmFieldError(
                'The string entered is bigger than the "max_length" defined ({})'.format(self.max_length)
            )
        return str(value)


class EmailField(CharField):
    def validate(self, value):
        super(EmailField, self).validate(value)
        # now validate the emailfield here
        email_regex = r"^[\w][\w0-9_.+-]+@[\w0-9-]+\.[\w0-9-.]+$"
        if not re.match(email_regex, value):
            raise AsyncOrmFieldError('"{}" not a valid email address'.format(value))


class TextField(Field):
    internal_type = str
    creation_string = "text"
    args = ("choices", "db_column", "db_index", "default", "null", "unique")

    def __init__(self, choices=None, db_column="", db_index=False, default=None, null=False, unique=False):
        super().__init__(
            choices=choices, db_column=db_column, db_index=db_index, default=default, null=null, unique=unique
        )


# numeric fields
class NumberField(Field):
    pass


class IntegerField(NumberField):
    internal_type = int
    creation_string = "integer"
    args = ("choices", "db_column", "db_index", "default", "null", "unique")

    def __init__(self, choices=None, db_column="", db_index=False, default=None, null=False, unique=False):
        super().__init__(
            choices=choices, db_column=db_column, db_index=db_index, default=default, null=null, unique=unique
        )


class BigIntegerField(IntegerField):
    creation_string = "bigint"


class FloatField(NumberField):
    internal_type = float
    creation_string = "double precision"
    args = ("choices", "db_column", "db_index", "default", "null", "unique")

    def __init__(self, choices=None, db_column="", db_index=False, default=None, null=False, unique=False):
        super().__init__(
            choices=choices, db_column=db_column, db_index=db_index, default=default, null=null, unique=unique
        )


class DecimalField(NumberField):
    internal_type = (Decimal, float, int)
    creation_string = "decimal({max_digits},{decimal_places})"
    args = ("choices", "db_column", "db_index", "decimal_places", "default", "null", "unique", "max_digits")

    def __init__(
        self,
        choices=None,
        db_column="",
        db_index=False,
        decimal_places=2,
        default=None,
        max_digits=10,
        null=False,
        unique=False,
    ):
        super().__init__(
            choices=choices,
            db_column=db_column,
            db_index=db_index,
            decimal_places=decimal_places,
            default=default,
            max_digits=max_digits,
            null=null,
            unique=unique,
        )


# time fields
class AutoField(IntegerField):
    creation_string = "serial PRIMARY KEY"
    args = ("choices", "db_column", "db_index", "default", "null", "unique")

    def __init__(self, db_column="id"):
        super().__init__(db_column=db_column, unique=True, null=False)


class DateTimeField(Field):
    internal_type = datetime
    creation_string = "timestamp"
    strftime = "%Y-%m-%d  %H:%s"
    args = ("auto_now", "choices", "db_column", "db_index", "default", "null", "strftime", "unique")

    def serialize_data(self, value):
        return value

    def __init__(
        self,
        auto_now=False,
        choices=None,
        db_column="",
        db_index=False,
        default=None,
        null=False,
        strftime=None,
        unique=False,
    ):
        super().__init__(
            auto_now=auto_now,
            choices=choices,
            db_column=db_column,
            db_index=db_index,
            default=default,
            null=null,
            strftime=strftime or self.strftime,
            unique=unique,
        )


class DateField(DateTimeField):
    internal_type = date
    creation_string = "date"
    args = ("auto_now", "choices", "db_column", "db_index", "default", "null", "strftime", "unique")
    strftime = "%Y-%m-%d"


class TimeField(DateTimeField):
    internal_type = time
    creation_string = "time"
    strftime = "%H:%s"


# relational fields
class ForeignKey(Field):
    internal_type = int
    required_kwargs = ["foreign_key"]
    creation_string = "integer references {foreign_key}"
    args = ("db_column", "db_index", "default", "foreign_key", "null", "unique")

    def __init__(self, db_column="", db_index=False, default=None, foreign_key="", null=False, unique=False):
        super().__init__(
            db_column=db_column, db_index=db_index, default=default, foreign_key=foreign_key, null=null, unique=unique
        )


class ManyToManyField(Field):
    internal_type = list, int
    required_kwargs = ["foreign_key"]
    creation_string = """
        {own_model} INTEGER REFERENCES {own_model} NOT NULL,
        {foreign_key} INTEGER REFERENCES {foreign_key} NOT NULL
    """
    args = ("db_column", "db_index", "default", "foreign_key", "unique")

    def __init__(self, db_column="", db_index=False, default=None, foreign_key=None, unique=False):
        super().__init__(
            db_column=db_column, db_index=db_index, default=default, foreign_key=foreign_key, unique=unique
        )

    def creation_query(self):
        return self.creation_string.format(**self.__dict__)

    def validate(self, value):
        if isinstance(value, list):
            for i in value:
                super().validate(i)
        else:
            super().validate(value)


# other data types
class JsonField(Field):
    internal_type = dict, list, str
    required_kwargs = ["max_length"]
    creation_string = "JSON"
    # creation_string = 'varchar({max_length})'
    args = ("choices", "db_column", "db_index", "default", "max_length", "null", "unique")

    def __init__(
        self, choices=None, db_column="", db_index=False, default=None, max_length=0, null=False, unique=False
    ):
        super().__init__(
            choices=choices,
            db_column=db_column,
            db_index=db_index,
            default=default,
            max_length=max_length,
            null=null,
            unique=unique,
        )

    @classmethod
    def recompose(cls, value):
        return json.loads(value)

    def sanitize_data(self, value):
        self.validate(value)

        if value is not None:
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except JSONDecodeError:
                    raise AsyncOrmFieldError("The data entered can not be converted to json")
            value = json.dumps(value)

        if len(value) > self.max_length:
            raise AsyncOrmFieldError(
                'The string entered is bigger than the "max_length" defined ({})'.format(self.max_length)
            )

        return value


class Uuid4Field(Field):
    internal_type = UUID
    args = ("db_column", "db_index", "null", "unique", "uuid_type")

    def __init__(self, db_column="", db_index=False, null=False, unique=True, uuid_type="v4"):
        self.field_requirement = 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'

        if uuid_type not in ["v1", "v4"]:
            raise AsyncOrmFieldError("{} is not a recognized type".format(uuid_type))

        super().__init__(
            db_column=db_column, db_index=db_index, default=None, null=null, unique=unique, uuid_type=uuid_type
        )

    @property
    def creation_string(self):
        uuid_types = {"v1": "uuid_generate_v1mc", "v4": "uuid_generate_v4"}
        return "UUID DEFAULT {}()".format(uuid_types[self.uuid_type])

    def sanitize_data(self, value):
        exp = r"^[a-zA-Z0-9\-\b]{36}$"
        if re.match(exp, value):
            return value
        raise AsyncOrmFieldError("The expression doesn't validate as a correct {}".format(self.__class__.__name__))


class ArrayField(Field):
    internal_type = list
    creation_string = "{value_type} ARRAY"
    args = ("db_column", "db_index", "default", "null", "unique", "value_type")
    value_types = ("text", "varchar", "integer")

    def __init__(self, db_column="", db_index=False, default=None, null=True, unique=False, value_type="text"):
        super().__init__(db_column=db_column, db_index=db_index, default=default, null=null, unique=unique)
        self.value_type = value_type

    def validate(self, value):
        super().validate(value)
        if value:
            items_type = self.homogeneous_type(value)
            if not items_type:
                raise AsyncOrmFieldError("Array elements are not of the same type")
            if items_type == list:
                if not all(len(item) == len(value[0]) for item in value):
                    raise AsyncOrmFieldError("Multi-dimensional arrays must have items of the same size")
        return value

    @staticmethod
    def homogeneous_type(value):
        iseq = iter(value)
        first_type = type(next(iseq))
        return first_type if all(isinstance(x, first_type) for x in iseq) else False


# network fields
class GenericIPAddressField(Field):
    internal_type = IPNetwork
    creation_string = "INET"
    args = ("db_column", "db_index", "null", "protocol", "unique", "unpack_protocol")

    def __init__(
        self, db_column="", db_index=False, null=False, protocol="both", unique=False, unpack_protocol="same"
    ):
        if protocol.lower() not in ("both", "ipv6", "ipv4"):
            raise AsyncOrmFieldError('"{}" is not a recognized protocol'.format(protocol))
        if unpack_protocol.lower() not in ("same", "ipv6", "ipv4"):
            raise AsyncOrmFieldError('"{}" is not a recognized unpack_protocol'.format(unpack_protocol))
        if protocol.lower() != "both" and unpack_protocol != "same":
            raise AsyncOrmFieldError(
                "if the protocol is restricted the output will always be in the same protocol version, "
                'so unpack_protocol should be default value, "same"'
            )

        super().__init__(
            db_column=db_column,
            db_index=db_index,
            default=None,
            null=null,
            protocol=protocol,
            unique=unique,
            unpack_protocol=unpack_protocol,
        )

    def validate(self, value):
        try:
            IPNetwork(value)
        except AddrFormatError:
            raise AsyncOrmFieldError("Not a correct IP address")

        if self.protocol.lower() != "both" and IPNetwork(value).version != int(self.protocol[-1:]):
            raise AsyncOrmFieldError("{} is not a correct {} IP address".format(value, self.protocol))

    def recompose(self, value):
        if value is not None:
            if self.unpack_protocol != "same":
                value = getattr(IPNetwork(str(value)), self.unpack_protocol)()
            value = str(value)
        return value

    def serialize_data(self, value):
        return self.recompose(value)

    def sanitize_data(self, value):
        return value


class MACAdressField(Field):
    internal_type = EUI
    creation_string = "MACADDR"
    args = ("db_column", "db_index", "default", "dialect", "null", "unique")
    mac_dialects = {
        "bare": mac_bare,
        "cisco": mac_cisco,
        "eui48": mac_eui48,
        "pgsql": mac_pgsql,
        "unix": mac_unix,
        "unix_expanded": mac_unix_expanded,
    }

    def __init__(self, db_column="", db_index=False, default=None, dialect="unix", null=False, unique=True):
        if dialect not in (self.mac_dialects.keys()):
            raise AsyncOrmFieldError('"{}" is not a correct mac dialect'.format(dialect))

        super().__init__(
            db_column=db_column, db_index=db_index, default=default, dialect=dialect, null=null, unique=unique
        )

    def validate(self, value):
        try:
            EUI(value)
        except AddrFormatError:
            raise AsyncOrmFieldError("Not a correct MAC address")

    def recompose(self, value):
        if value is not None:
            v = EUI(value)
            v.dialect = self.mac_dialects[self.dialect]
            return str(v)
        return value

    def sanitize_data(self, value):
        return value
