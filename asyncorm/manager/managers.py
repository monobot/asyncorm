from asyncpg.exceptions import UniqueViolationError

from ..exceptions import QuerysetError, ModelError
from ..fields import ManyToMany, ForeignKey, CharField  # , ManyToMany
from ..database import Cursor
# from .log import logger

__all__ = ['ModelManager', 'Queryset']

LOOKUP_OPERATOR = {
    'gt': '{} > {}',
    'lt': '{} < {}',
    'gte': '{} >= {}',
    'lte': '{} <= {}',
    'range': '({k}>{min} AND {k}<{max})',
    'in': '{} = ANY (array[{}])',
    'exact': '{} LIKE {}',
    'iexact': '{} ILIKE {}',
    'contains': '{} LIKE \'%{}%\'',
    'icontains': '{} ILIKE \'%{}%\'',
    'startswith': '{} LIKE \'{}%\'',
    'istartswith': '{} ILIKE \'{}%\'',
    'endswith': '{} LIKE \'%{}\'',
    'iendswith': '{} ILIKE \'%{}\'',
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

    @property
    def basic_query(self):
        return [{
            'action': 'db__select_all',
            'select': '*',
            'table_name': self.model.cls_tablename(),
            'ordering': []
        }]

    @classmethod
    def set_orm(cls, orm):
        cls.orm = orm
        cls.db_manager = orm.db_manager

    def get_field_queries(self):
        # Builds the creationquery for each of the non fk or m2m fields
        return ', '.join([
            f.creation_query() for f in self.model.fields.values()
            if not isinstance(f, ManyToMany) and
            not isinstance(f, ForeignKey)
        ])

    def create_table_builder(self):
        return [{
            'table_name': self.model.cls_tablename(),
            'action': 'db__create_table',
            'field_queries': self.get_field_queries(),
        }]

    async def create_table(self):
        '''
        Builds the table without the m2m_fields and fks
        '''
        await self.db_request(self.create_table_builder())

    async def unique_together(self):
        '''
        Builds the unique together constraint
        '''
        unique_together = self.get_unique_together()

        if unique_together:
            db_request = [{
                'table_name': self.model.cls_tablename(),
                'action': 'db__constrain_table',
                'constrain': unique_together,
            }]

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

    def add_m2m_columns_builder(self, field):
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
            if isinstance(f, ManyToMany):
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
            data.update({k: v})

        instance.construct(data)
        return instance

    async def queryset(self):
        return await self.all()

    def all(self):
        queryset = self
        if not self.query:
            queryset = self._copy_me()

        return queryset

    async def count(self):
        if self.query is None:
            self.query = self.basic_query
        query = self.query[:]
        query[0]['select'] = 'COUNT(*)'

        resp = await self.db_request(query)
        for v in resp.values():
            return v

    async def get(self, **kwargs):
        data = self.filter(**kwargs)
        length = await data.count()
        if length:
            if length > 1:
                raise QuerysetError(
                    'More than one {} where returned, there are {}!'.format(
                        self.model.__name__,
                        length,
                    )
                )

            async for itm in self.filter(**kwargs):
                return itm
        raise QuerysetError(
            'That {} does not exist'.format(self.model.__name__)
        )

    def calc_filters(self, kwargs, exclude):
        # recompose the filters
        bool_string = exclude and 'NOT ' or ''
        filters = []

        for k, v in kwargs.items():
            # we format the key, the conditional and the value
            operator = '{} = {}'
            lookup = None
            if len(k.split('__')) > 1:
                k, lookup = k.split('__')
                operator = LOOKUP_OPERATOR[lookup]

            field = getattr(self.model, k)

            string_lookups = [
                'contains', 'icontains', 'startswith', 'istartswith',
                'endswith', 'iendswith',
            ]

            if operator == '({k}>{min} AND {k}<{max})':
                if not isinstance(v, (tuple, list)):
                    raise QuerysetError(
                        '{} should be list or a tuple'.format(lookup)
                    )
                if len(v) != 2:
                    raise QuerysetError(
                        'Not a correct tuple/list definition, '
                        'should be of size 2'
                    )
                filters.append(
                    bool_string +
                    '({k}>{min} AND {k}<{max})'.format(
                        k=field.field_name,
                        min=field.sanitize_data(v[0]),
                        max=field.sanitize_data(v[1]),
                    )
                )
            elif lookup in string_lookups:
                is_charfield = isinstance(field, CharField)
                # is_othercharfield = issubclass(field, CharField)
                # if not is_charfield or not is_othercharfield:
                if not is_charfield:
                    raise QuerysetError(
                        '{} not allowed in non CharField fields'.format(lookup)
                    )
                v = field.sanitize_data(v)[1:-2]
                filters.append(
                    bool_string + operator.format(field.field_name, v)
                )
            else:
                if isinstance(v, (list, tuple)):
                    # check they are correct items and serialize
                    v = ','.join([str(field.sanitize_data(si)) for si in v])
                else:
                    v = field.sanitize_data(v)

                filters.append(
                    bool_string + operator.format(field.field_name, v)
                )

        return filters

    def filter(self, exclude=False, **kwargs):
        filters = self.calc_filters(kwargs, exclude)
        condition = ' AND '.join(filters)

        queryset = self.all()

        queryset.query.append({'action': 'db__where', 'condition': condition})
        return queryset

    def exclude(self, **kwargs):
        return self.filter(exclude=True, **kwargs)

    async def db_request(self, db_request):
        db_request = db_request[:]
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
            return self

        elif isinstance(key, int):
            # if its an int, the developer wants the object directly
            if key < 0:
                raise QuerysetError('Negative indices are not allowed')

            conn = await self.db_manager.get_conn()

            cursor = self._cursor
            if not cursor:
                query = self.db_manager.construct_query(self.query[:])
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
            query = self.db_manager.construct_query(self.query[:])
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

        queryset.query = self.basic_query

        if self.model.ordering:
            queryset.query[0].update({'ordering': self.model.ordering})

        queryset.set_orm(self.orm)

        return queryset

    async def save(self, instanced_model):
        # performs the database save
        fields, field_data = [], []
        for k, data in instanced_model.data.items():
            f_class = getattr(instanced_model.__class__, k)

            field_name = f_class.field_name or k
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
        await n_object.save()

        return n_object
