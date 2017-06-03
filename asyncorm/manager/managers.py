from asyncpg.exceptions import UniqueViolationError
from copy import deepcopy

from ..exceptions import (
    ModelDoesNotExist, ModelError, MultipleObjectsReturned, QuerysetError,
)

from ..models.fields import ManyToManyField, ForeignKey, CharField, NumberField
from ..database import Cursor
# from .log import logger

__all__ = ['ModelManager', 'Queryset']

LOOKUP_OPERATOR = {
    'gt': '{t_n}.{k} > {v}',
    'lt': '{t_n}.{k} < {v}',
    'gte': '{t_n}.{k} >= {v}',
    'lte': '{t_n}.{k} <= {v}',
    'range': '({t_n}.{k}>={min} AND {t_n}.{k}<={max})',
    'in': '{t_n}.{k} = ANY (array[{v}])',
    'exact': '{t_n}.{k} LIKE \'{v}\'',
    'iexact': '{t_n}.{k} ILIKE \'{v}\'',
    'contains': '{t_n}.{k} LIKE \'%{v}%\'',
    'icontains': '{t_n}.{k} ILIKE \'%{v}%\'',
    'startswith': '{t_n}.{k} LIKE \'{v}%\'',
    'istartswith': '{t_n}.{k} ILIKE \'{v}%\'',
    'endswith': '{t_n}.{k} LIKE \'%{v}\'',
    'iendswith': '{t_n}.{k} ILIKE \'%{v}\'',
    'regex': '{t_n}.{k} ~ {v}',
    'iregex': '{t_n}.{k} ~* {v}',
}


class Queryset(object):
    db_manager = None
    orm = None

    def __init__(self, model):
        self.model = model

        self.table_name = self.model.cls_tablename()
        self.select = '*'

        self.query = None

        self._cursor = None
        self._results = []

        self.forward = 0
        self.stop = None
        self.step = None

    def query_copy(self):
        return (
            self.query and deepcopy(self.query) or deepcopy(self.basic_query)
        )

    @property
    def basic_query(self):
        return [{
            'action': 'db__select_all',
            'select': '*',
            'table_name': self.model.cls_tablename(),
            'ordering': self.model.ordering,
            'join': '',
        }]

    @classmethod
    def set_orm(cls, orm):
        cls.orm = orm
        cls.db_manager = orm.db_manager

    def get_field_queries(self):
        '''Builds the creationquery for each of the non fk or m2m fields'''
        return ', '.join([
            f.creation_query() for f in self.model.fields.values()
            if not isinstance(f, ManyToManyField) and
            not isinstance(f, ForeignKey)
        ])

    def create_table_builder(self):
        return [{
            'table_name': self.model.cls_tablename(),
            'action': 'db__create_table',
            'field_queries': self.get_field_queries(),
        }]

    async def create_table(self):
        '''Builds the table without the m2m_fields and fks'''
        await self.db_request(self.create_table_builder())

    def unique_together_builder(self):
        unique_together = self.get_unique_together()

        if unique_together:
            return [{
                'table_name': self.model.cls_tablename(),
                'action': 'db__constrain_table',
                'constrain': unique_together,
            }]
        return None

    async def unique_together(self):
        '''Builds the unique together constraint'''
        db_request = self.unique_together_builder()

        if db_request:
            await self.db_request(db_request)

    def add_fk_field_builder(self, field):
        return [{
            'table_name': self.model.cls_tablename(),
            'action': 'db__table_add_column',
            'field_creation_string': field.creation_query(),
        }]

    async def add_fk_columns(self):
        '''
        Builds the fk fields
        '''
        for f in self.model.fields.values():
            if isinstance(f, ForeignKey):
                await self.db_request(self.add_fk_field_builder(f))

    @staticmethod
    def add_m2m_columns_builder(field):
        return [{
            'table_name': field.table_name,
            'action': 'db__create_table',
            'field_queries': field.creation_query(),
        }]

    async def add_m2m_columns(self):
        '''
        Builds the m2m_fields
        '''
        for f in self.model.fields.values():
            if isinstance(f, ManyToManyField):
                await self.db_request(self.add_m2m_columns_builder(f))

    def get_unique_together(self):
        # builds the table with all its fields definition
        unique_string = ' UNIQUE ({}) '.format(
            ','.join(self.model.unique_together)
        )
        return self.model.unique_together and unique_string or ''

    def modelconstructor(self, record, instance=None):
        if not instance:
            instance = self.model()

        data = {}
        for k, v in record.items():
            select_related = []
            splitted = k.split('__')
            if len(splitted) > 1:
                if splitted[0] not in select_related:
                    select_related.append(splitted[0])
            else:
                data.update({k: v})

        if select_related:
            pass

        instance.construct(data, subitems=self.query)
        return instance

    #               QUERYSET METHODS
    #               ENDING QUERYSETS
    async def count(self):
        query = self.query_copy()
        query[0]['select'] = 'COUNT(*)'

        resp = await self.db_request(query)
        for v in resp.values():
            return v

    async def exists(self):
        query = self.query_copy()
        query[0]['action'] = 'db__exists'

        resp = await self.db_request(query)
        for v in resp.values():
            return v

    async def calculate(self, field_name, operation):
        if hasattr(self.model, field_name):
            field = getattr(self.model, field_name)
        else:
            raise QuerysetError(
                '{} wrong field name for model {}'.format(
                    field_name,
                    self.model.__name__
                )
            )
        if not isinstance(field, NumberField):
            raise QuerysetError('{} is not a numeric field'.format(field_name))

        query = self.query_copy()
        query[0]['select'] = '{}({})'.format(operation, field_name)

        resp = await self.db_request(query)
        for v in resp.values():
            return v

    async def Max(self, field_name):
        return await self.calculate(field_name, 'MAX')

    async def Min(self, field_name):
        return await self.calculate(field_name, 'MIN')

    async def Sum(self, field_name):
        return await self.calculate(field_name, 'SUM')

    async def Avg(self, field_name):
        return await self.calculate(field_name, 'AVG')

    async def StdDev(self, field_name):
        return await self.calculate(field_name, 'STDDEV')

    async def get(self, **kwargs):
        queryset = self.queryset().filter(**kwargs)

        count = await queryset.count()

        if count > 1:
            raise MultipleObjectsReturned(
                'More than one {} where returned, there are {}!'.format(
                    self.model.__name__,
                    count,
                )
            )
        elif not count:
            raise self.model.DoesNotExist(
                'That {} does not exist'.format(self.model.__name__)
            )

        queryset = self.queryset()
        async for itm in queryset.filter(**kwargs):
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
        select_related = {'action': 'db__select_related', 'fields': []}
        for arg in args:
            # fr the time been we overlook the after the '__'
            if '__' in arg:
                arg = arg.split('__')[0]
            if not hasattr(self.model, arg):
                raise QuerysetError(
                    '{} is not a {} attribute.'.format(
                        arg,
                        self.model.__name__
                    )
                )
            if not isinstance(getattr(self.model, arg), ForeignKey):
                raise QuerysetError(
                    '{} is not a ForeignKey Field for {}.'.format(
                        arg,
                        self.model.__name__
                    )
                )
            model = self.orm.get_model(getattr(self.model, arg).foreign_key)

            right_table = model.table_name or model.__name__.lower()
            left_table = self.model.table_name or self.model.__name__.lower()

            fields_formatter = ', '.join([
                '{right_table}.{field} AS {right_table}€$$€{field}'.format(
                    right_table=right_table,
                    field=field
                ) for field in model.get_db_columns()

            ])
            select_related['fields'].append(
                {
                    'right_table': right_table,
                    'left_table': left_table,
                    'foreign_field': arg,
                    'model_db_pk': model.db_pk,
                    'fields_formatter': fields_formatter,
                    'orm_fieldname': arg,
                }
            )
        queryset = self._copy_me()
        queryset.query.append(select_related)

        return queryset

    def calc_filters(self, kwargs, exclude):
        # recompose the filters
        bool_string = exclude and 'NOT ' or ''
        filters = []

        for k, v in kwargs.items():
            # we format the key, the conditional and the value
            operator = '{t_n}.{k} = {v}'
            lookup = None
            if len(k.split('__')) > 1:
                k, lookup = k.split('__')
                operator = LOOKUP_OPERATOR[lookup]

            field = getattr(self.model, k)

            string_lookups = [
                'exact', 'iexact',
                'contains', 'icontains',
                'startswith', 'istartswith', 'endswith', 'iendswith',
            ]

            operator_formater = {
                't_n': self.model.table_name or self.model.__name__.lower(),
                'k': field.db_column,
                'v': v
            }
            if operator == '({t_n}.{k}>={min} AND {t_n}.{k}<={max})':
                if not isinstance(v, (tuple, list)):
                    raise QuerysetError(
                        '{} should be list or a tuple'.format(lookup)
                    )
                if len(v) != 2:
                    raise QuerysetError(
                        'Not a correct tuple/list definition, '
                        'should be of size 2'
                    )
                operator_formater.update({
                    'min': field.sanitize_data(v[0]),
                    'max': field.sanitize_data(v[1]),
                })
            elif lookup in string_lookups:
                is_charfield = isinstance(field, CharField)
                # is_othercharfield = issubclass(field, CharField)
                # if not is_charfield or not is_othercharfield:
                if not is_charfield:
                    raise QuerysetError(
                        '{} not allowed in non CharField fields'.format(lookup)
                    )
                operator_formater['v'] = field.sanitize_data(v)[1:-1]
            else:
                if isinstance(v, (list, tuple)):
                    # check they are correct items and serialize
                    v = ','.join([str(field.sanitize_data(si)) for si in v])
                else:
                    v = field.sanitize_data(v)
                operator_formater['v'] = v

            filters.append(
                bool_string +
                operator.format(**operator_formater)
            )

        return filters

    def filter(self, exclude=False, **kwargs):
        filters = self.calc_filters(kwargs, exclude)
        condition = ' AND '.join(filters)

        queryset = self.queryset()

        queryset.query.append({'action': 'db__where', 'condition': condition})
        return queryset

    def exclude(self, **kwargs):
        return self.filter(exclude=True, **kwargs)

    def only(self, *args):
        # retrieves from the database only the attrs requested
        # all the rest come as None
        for arg in args:
            if not hasattr(self.model, arg):
                raise QuerysetError(
                    '{} is not a correct field for {}'.format(
                        arg, self.model.__name__
                    )
                )

        queryset = self.queryset()
        queryset.query = self.query_copy()
        queryset.query[0]['select'] = ','.join(args)

        return queryset

    def order_by(self, *args):
        # retrieves from the database only the attrs requested
        # all the rest come as None
        final_args = []
        for arg in args:
            if arg[0] == '-':
                arg = arg[1:]
                final_args.append('-' + arg)
            else:
                final_args.append(arg)

            if not hasattr(self.model, arg):
                raise QuerysetError(
                    '{} is not a correct field for {}'.format(
                        arg, self.model.__name__
                    )
                )

        queryset = self.queryset()
        queryset.query = self.query_copy()
        queryset.query[0]['ordering'] = final_args

        return queryset

    async def latest_migration(self):
        kwargs = {
            'select': '*',
            'table_name': 'asyncorm_migrations',
            'join': '',
            'ordering': 'ORDER BY  -id',
            'condition': "app = '{}'".format(self.model().app_name)
        }

        results = await self.db_manager.request(
            self.db_manager.db__select.format(**kwargs)
        )

        for k, v in results.items():
            if k == 'name':
                return int(v)

    #               DB RELAED METHODS
    async def db_request(self, db_request):
        db_request = deepcopy(db_request)
        db_request[0].update({
            'select': db_request[0].get('select', self.select),
            'table_name': db_request[0].get(
                'table_name', self.model.cls_tablename()
            ),
        })
        query = self.db_manager.construct_query(db_request)
        return await self.db_manager.request(query)

    async def __getitem__(self, key):
        if isinstance(key, slice):
            # control the keys values
            if key.start is not None and key.start < 0:
                raise QuerysetError('Negative indices are not allowed')
            if key.stop is not None and key.stop < 0:
                raise QuerysetError('Negative indices are not allowed')
            if key.step is not None:
                raise QuerysetError('step on Queryset is not allowed')

            # asign forward and stop to the modelmanager and return it
            self.forward = key.start
            self.stop = key.stop
            if key.start is None:
                self.forward = 0
            return self

        elif isinstance(key, int):
            # if its an int, the developer wants the object directly
            if key < 0:
                raise QuerysetError('Negative indices are not allowed')

            conn = await self.db_manager.get_conn()

            cursor = self._cursor
            if not cursor:
                query = self.db_manager.construct_query(deepcopy(self.query))
                cursor = Cursor(
                    conn,
                    query,
                    forward=key,
                )

            async for res in cursor:
                return self.modelconstructor(res)
            raise IndexError(
                'That {} index does not exist'.format(self.model.__name__)
            )

        else:
            raise TypeError("Invalid argument type.")

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self._cursor:
            conn = await self.db_manager.get_conn()
            query = self.db_manager.construct_query(self.query)
            self._cursor = Cursor(
                conn,
                query,
                forward=self.forward,
                stop=self.stop,
            )

        async for rec in self._cursor:
            item = self.modelconstructor(rec)
            return item
        raise StopAsyncIteration()


class ModelManager(Queryset):

    def __init__(self, model, field=None):
        self.model = model
        self.field = field
        super().__init__(model)

    def _copy_me(self):
        queryset = ModelManager(self.model)
        queryset.set_orm(self.orm)
        queryset.query = self.query_copy()

        return queryset

    async def get_or_create(self, **kwargs):
        try:
            return await self.get(**kwargs), False
        except ModelDoesNotExist:
            return await self.create(**kwargs), True

    async def save(self, instanced_model):
        # performs the database save
        fields, field_data = [], []
        for k, data in instanced_model.data.items():
            f_class = getattr(instanced_model.__class__, k)

            field_name = f_class.db_column or k
            data = f_class.sanitize_data(data)

            fields.append(field_name)
            field_data.append(data)

        db_request = [{
            'action': (
                getattr(
                    instanced_model, instanced_model.orm_pk
                ) and 'db__update' or 'db__insert'
            ),
            'id_data': '{}={}'.format(
                instanced_model.db_pk,
                getattr(instanced_model, instanced_model.orm_pk),
            ),
            'field_names': ', '.join(fields),
            'field_values': ', '.join(field_data),
            'condition': '{}={}'.format(
                instanced_model.db_pk,
                getattr(instanced_model, instanced_model.orm_pk)
            )
        }]
        try:
            response = await self.db_request(db_request)
        except UniqueViolationError:
            raise ModelError('The model violates a unique constraint')

        self.modelconstructor(response, instanced_model)

        # now we have to save the m2m relations: m2m_data
        fields, field_data = [], []
        for k, data in instanced_model.m2m_data.items():
            # for each of the m2m fields in the model, we have to check
            # if the table register already exists in the table otherwise
            # and delete the ones that are not in the list
            # first get the table_name
            cls_field = getattr(instanced_model.__class__, k)
            table_name = cls_field.table_name
            foreign_column = cls_field.foreign_key

            model_column = instanced_model.cls_tablename()

            model_id = getattr(instanced_model, instanced_model.orm_pk)

            db_request = [{
                'table_name': table_name,
                'action': 'db__insert',
                'field_names': ', '.join([model_column, foreign_column]),
                'field_values': ', '.join([str(model_id), str(data)]),
            }]

            if isinstance(data, list):
                for d in data:
                    db_request[0].update(
                        {'field_values': ', '.join([str(model_id), str(d)])}
                    )
                    await self.db_request(db_request)
            else:
                await self.db_request(db_request)

    async def delete(self, instanced_model):
        db_request = [{
            'action': 'db__delete',
            'id_data': '{}={}'.format(
                instanced_model.db_pk,
                getattr(instanced_model, instanced_model.db_pk)
            )
        }]
        return await self.db_request(db_request)

    async def create(self, **kwargs):
        n_object = self.model(**kwargs)
        await self.model.objects.save(n_object)
        return n_object
