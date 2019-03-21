import datetime
from copy import deepcopy

from asyncpg.exceptions import InsufficientPrivilegeError

from asyncorm.exceptions import AsyncOrmModelError, AsyncOrmMultipleObjectsReturned, AsyncOrmQuerysetError
from asyncorm.manager.constants import LOOKUP_OPERATOR
from asyncorm.models.fields import CharField, ForeignKey, ManyToManyField, NumberField


class Queryset(object):
    db_backend = None
    orm = None

    def __init__(self, model):
        self.model = model

        self.table_name = self.model.cls_tablename()
        self.select = "*"

        self.query = None

        self._cursor = None
        self._results = []

        self.forward = 0
        self.stop = None
        self.step = None

    def query_copy(self):
        return self.query and deepcopy(self.query) or deepcopy(self.basic_query)

    @property
    def basic_query(self):
        return [
            {
                "action": "_db__select_all",
                "select": "*",
                "table_name": self.model.cls_tablename(),
                "ordering": self.model.ordering,
                "join": "",
            }
        ]

    @classmethod
    def set_orm(cls, orm):
        cls.orm = orm
        cls.db_backend = orm.db_backend

    def get_field_queries(self):
        """Builds the creationquery for each of the non fk or m2m fields"""
        return ", ".join(
            [
                f.creation_query()
                for f in self.model.fields.values()
                if not isinstance(f, (ManyToManyField, ForeignKey))
            ]
        )

    def create_table_builder(self):
        return [
            {
                "table_name": self.model.cls_tablename(),
                "action": "_db__create_table",
                "field_queries": self.get_field_queries(),
            }
        ]

    async def create_table(self):
        """Builds the table without the m2m_fields and fks"""
        await self.db_request(self.create_table_builder())

    async def set_requirements(self):
        """Add to the database the table requirements if needed"""
        try:
            for query in self.model.field_requirements:
                await self.db_backend.request(query)
        except InsufficientPrivilegeError:
            raise AsyncOrmModelError("Not enough privileges to add the needed requirement in the database")

    def unique_together_builder(self):
        unique_together = self.get_unique_together()

        if unique_together:
            return [
                {
                    "table_name": self.model.cls_tablename(),
                    "action": "_db__constrain_table",
                    "constrain": unique_together,
                }
            ]
        return None

    async def unique_together(self):
        """Builds the unique together constraint"""
        db_request = self.unique_together_builder()

        if db_request:
            await self.db_request(db_request)

    def add_fk_field_builder(self, field):
        return [
            {
                "table_name": self.model.cls_tablename(),
                "action": "db__table_add_column",
                "field_creation_string": field.creation_query(),
            }
        ]

    async def add_fk_columns(self):
        """
        Builds the fk fields
        """
        for f in self.model.fields.values():
            if isinstance(f, ForeignKey):
                await self.db_request(self.add_fk_field_builder(f))

    @staticmethod
    def _add_m2m_columns_builder(field):
        return [
            {"table_name": field.table_name, "action": "_db__create_table", "field_queries": field.creation_query()}
        ]

    @staticmethod
    def _add_table_indices_builder(field):
        return [
            {
                "index_name": "idx_{}_{}".format(field.table_name, field.orm_field_name)[:30],
                "table_name": field.table_name,
                "action": "_db__create_field_index",
                "colum_name": field.orm_field_name,
            }
        ]

    async def add_m2m_columns(self):
        """
        Builds the m2m_fields
        """
        for f in self.model.fields.values():
            if isinstance(f, ManyToManyField):
                await self.db_request(self._add_m2m_columns_builder(f))

    async def add_table_indices(self):
        for f in self.model.fields.values():
            if f.db_index:
                await self.db_request(self._add_table_indices_builder(f))

    def get_unique_together(self):
        # builds the table with all its fields definition
        unique_string = " UNIQUE ({}) ".format(",".join(self.model.unique_together))
        return self.model.unique_together and unique_string or ""

    def modelconstructor(self, record, instance=None):
        if not instance:
            instance = self.model()

        data = {}
        for k, v in record.items():
            select_related = []
            splitted = k.split("__")
            if len(splitted) > 1:
                if splitted[0] not in select_related:
                    select_related.append(splitted[0])
            else:
                data.update({k: v})

        if select_related:
            pass

        instance.construct(data, subitems=self.query)
        return instance

    async def count(self):
        query = self.query_copy()
        query[0]["select"] = "COUNT(*)"

        resp = await self.db_request(query)
        for v in resp.values():
            return v

    async def exists(self):
        query = self.query_copy()
        query[0]["action"] = "_db__exists"

        resp = await self.db_request(query)
        for v in resp.values():
            return v

    async def calculate(self, field_name, operation):
        if hasattr(self.model, field_name):
            field = getattr(self.model, field_name)
        else:
            raise AsyncOrmQuerysetError("{} wrong field name for model {}".format(field_name, self.model.__name__))
        if not isinstance(field, NumberField):
            raise AsyncOrmQuerysetError("{} is not a numeric field".format(field_name))

        query = self.query_copy()
        query[0]["select"] = "{}({})".format(operation, field_name)

        resp = await self.db_request(query)
        for v in resp.values():
            return v

    async def Max(self, field_name):
        return await self.calculate(field_name, "MAX")

    async def Min(self, field_name):
        return await self.calculate(field_name, "MIN")

    async def Sum(self, field_name):
        return await self.calculate(field_name, "SUM")

    async def Avg(self, field_name):
        return await self.calculate(field_name, "AVG")

    async def StdDev(self, field_name):
        return await self.calculate(field_name, "STDDEV")

    async def get(self, **kwargs):
        count = 0
        queryset = self.queryset().filter(**kwargs)

        async for itm in queryset:
            count += 1

        if count > 1:
            raise AsyncOrmMultipleObjectsReturned(
                'More than one "{}" were returned, there are {}!'.format(self.model.__name__, count)
            )
        elif count == 0:
            raise self.model.DoesNotExist("That {} does not exist".format(self.model.__name__))

        return itm

    #               CHAINABLE QUERYSET METHODS
    def queryset(self):
        return self._copy_me()

    def all(self):
        return self._copy_me()

    def none(self):
        queryset = self._copy_me()

        kwargs = {self.model.db_pk: -1}
        return queryset.filter(**kwargs)

    def select_related(self, *args):
        select_related = {"action": "_db__select_related", "fields": []}
        for arg in args:
            # fr the time been we overlook the after the '__'
            if "__" in arg:
                arg = arg.split("__")[0]
            if not hasattr(self.model, arg):
                raise AsyncOrmQuerysetError("{} is not a {} attribute.".format(arg, self.model.__name__))
            if not isinstance(getattr(self.model, arg), ForeignKey):
                raise AsyncOrmQuerysetError("{} is not a ForeignKey Field for {}.".format(arg, self.model.__name__))
            model = self.orm.get_model(getattr(self.model, arg).foreign_key)

            right_table = model.table_name or model.__name__.lower()
            left_table = self.model.table_name or self.model.__name__.lower()

            fields_formatter = ", ".join(
                [
                    "{right_table}.{field} AS {right_table}€$$€{field}".format(right_table=right_table, field=field)
                    for field in model.get_db_columns()
                ]
            )
            select_related["fields"].append(
                {
                    "right_table": right_table,
                    "left_table": left_table,
                    "foreign_field": arg,
                    "model_db_pk": model.db_pk,
                    "fields_formatter": fields_formatter,
                    "orm_fieldname": arg,
                }
            )
        queryset = self._copy_me()
        queryset.query.append(select_related)

        return queryset

    def calc_filters(self, kwargs, exclude):
        # recompose the filters
        bool_string = exclude and "NOT " or ""
        filters = []

        for k, v in kwargs.items():
            # we format the key, the conditional and the value
            operator = "{t_n}.{k} = {v}"
            lookup = None
            if len(k.split("__")) > 1:
                k, lookup = k.split("__")
                operator = LOOKUP_OPERATOR[lookup]

            field = getattr(self.model, k)

            string_lookups = [
                "exact",
                "iexact",
                "contains",
                "icontains",
                "startswith",
                "istartswith",
                "endswith",
                "iendswith",
            ]
            operator_formater = {
                "t_n": self.model.table_name or self.model.__name__.lower(),
                "k": field.db_column,
                "v": v,
            }
            if operator == "({t_n}.{k}>={min} AND {t_n}.{k}<={max})":
                if not isinstance(v, (tuple, list)):
                    raise AsyncOrmQuerysetError("{} should be list or a tuple".format(lookup))
                if len(v) != 2:
                    raise AsyncOrmQuerysetError("Not a correct tuple/list definition, should be of size 2")
                operator_formater.update({"min": field.sanitize_data(v[0]), "max": field.sanitize_data(v[1])})
            elif lookup in string_lookups:
                is_charfield = isinstance(field, CharField)
                # is_othercharfield = issubclass(field, CharField)
                # if not is_charfield or not is_othercharfield:
                if not is_charfield:
                    raise AsyncOrmQuerysetError("{} not allowed in non CharField fields".format(lookup))
                operator_formater["v"] = field.sanitize_data(v)
            else:
                if isinstance(v, (list, tuple)):
                    # check they are correct items and serialize
                    v = ",".join(
                        ["'{}'".format(field.sanitize_data(si)) if isinstance(si, str) else str(si) for si in v]
                    )
                elif v is None:
                    v = field.sanitize_data(v)[1:-1]
                    operator = operator.replace("=", "IS")
                elif isinstance(v, (datetime.datetime, datetime.date)) or isinstance(field, (CharField)):
                    v = "'{}'".format(v)
                else:
                    v = field.sanitize_data(v)
                operator_formater["v"] = v

            filters.append(bool_string + operator.format(**operator_formater))

        return filters

    def filter(self, exclude=False, **kwargs):
        filters = self.calc_filters(kwargs, exclude)
        condition = " AND ".join(filters)

        queryset = self.queryset()

        queryset.query.append({"action": "_db__where", "condition": condition})
        return queryset

    def exclude(self, **kwargs):
        return self.filter(exclude=True, **kwargs)

    def only(self, *args):
        # retrieves from the database only the attrs requested
        # all the rest come as None
        for arg in args:
            if not hasattr(self.model, arg):
                raise AsyncOrmQuerysetError("{} is not a correct field for {}".format(arg, self.model.__name__))

        queryset = self.queryset()
        queryset.query = self.query_copy()
        queryset.query[0]["select"] = ",".join(args)

        return queryset

    def order_by(self, *args):
        # retrieves from the database only the attrs requested
        # all the rest come as None
        final_args = []
        for arg in args:
            if arg[0] == "-":
                arg = arg[1:]
                final_args.append("-" + arg)
            else:
                final_args.append(arg)

            if not hasattr(self.model, arg):
                raise AsyncOrmQuerysetError("{} is not a correct field for {}".format(arg, self.model.__name__))

        queryset = self.queryset()
        queryset.query = self.query_copy()
        queryset.query[0]["ordering"] = final_args

        return queryset

    # DB RELATED METHODS
    async def db_request(self, db_request):
        db_request = deepcopy(db_request)
        db_request[0].update(
            {
                "select": db_request[0].get("select", self.select),
                "table_name": db_request[0].get("table_name", self.model.cls_tablename()),
            }
        )
        query = self.db_backend._construct_query(db_request)
        return await self.db_backend.request(query)

    def _get_queryset_slice(self, queryset_slice):
        """Private method to get a slice given the original queryset.

        :param queryset_slice: Slice to be retrieved
        :type queryset_slice: slice

        :return: The slice of the queryset
        :rtype: Queryset
        """
        self.forward = queryset_slice.start
        self.stop = queryset_slice.stop
        if queryset_slice.start is None:
            self.forward = 0
        return self

    async def _get_item(self, key):
        """Return the item selected from the iterator.

        :param key: The position in the slice
        :type key: int
        :raises IndexError: When the item selected does not exist in the slice
        :return: Model object from the Queryset
        :rtype: Model
        """
        if not self._cursor:
            self._cursor = await self.db_backend.get_cursor(deepcopy(self.query), forward=key, stop=None)

        async for res in self._cursor:
            return self.modelconstructor(res)

        raise IndexError("That {} index does not exist".format(self.model.__name__))

    async def __getitem__(self, key):
        if isinstance(key, slice):
            wrong_start_key = key.start is not None and key.start < 0
            wrong_stop_key = key.stop is not None and key.stop < 0
            if wrong_start_key or wrong_stop_key:
                raise AsyncOrmQuerysetError("Negative indices are not allowed")

            if key.step is not None:
                raise AsyncOrmQuerysetError("Step on Queryset is not allowed")

            return self._get_queryset_slice(key)

        elif isinstance(key, int):
            if key < 0:
                raise AsyncOrmQuerysetError("Negative indices are not allowed")

            return await self._get_item(key)

        else:
            raise TypeError("Invalid argument type.")

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._cursor:
            self._cursor = await self.db_backend.get_cursor(self.query, forward=self.forward, stop=self.stop)

        async for rec in self._cursor:
            item = self.modelconstructor(rec)
            return item

        raise StopAsyncIteration()
