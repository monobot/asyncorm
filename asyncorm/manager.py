from asyncpg.exceptions import UniqueViolationError

from .exceptions import QuerysetError, ModelError
from .fields import ManyToMany

__all__ = ['ModelManager', ]

MIDDLE_OPERATOR = {
    'gt': '>',
    'lt': '<',
    'gte': '>=',
    'lte': '<=',
}


class Queryset(object):
    model = None
    db_manager = None
    queryset = ''

    def _copy_me(self):
        queryset = Queryset()
        queryset.model = self.model
        return queryset

    def _creation_query(self):
        constraints = self._get_field_constraints()
        unique_together = self._get_unique_together()

        query = (
            'CREATE TABLE {table_name} ({field_queries}{unique_together});'
            '{constraints}{ending}'
        ).format(
            table_name=self.model.table_name,
            field_queries=self._get_field_queries(),
            unique_together=unique_together,
            constraints=constraints,
            ending=constraints and ';' or '',
        )
        # print(query)
        return query

    def _get_field_queries(self):
        # builds the table with all its fields definition
        return ', '.join(
            [f._creation_query() for f in self.model.fields.values()
            if not isinstance(f, ManyToMany)]
        )

    def _get_field_constraints(self):
        # builds the table with all its fields definition
        return '; '.join(
            [f._field_constraints() for f in self.model.fields.values()]
        )

    def _get_unique_together(self):
        # builds the table with all its fields definition
        unique_string = ', UNIQUE ({}) '.format(
            ','.join(self.model._unique_together)
        )
        return self.model._unique_together and unique_string or ''

    def _get_m2m_field_queries(self):
        # builds the relational many to many table
        return '; '.join(
            [f._creation_query() for f in self.model.fields.values()
            if isinstance(f, ManyToMany)]
        )

    def _construct_model(self, record, instance=None):
        if not instance:
            instance = self.model()

        data = {}
        for k, v in record.items():
            data.update({k: v})

        instance._construct(data)
        return instance

    async def queryset(self):
        return await self.all()

    async def all(self):
        db_request = {
            'table_name': self.model.table_name,
            'action': 'db__select_all',
        }

        request = await self.db_manager.request(db_request)
        return [self._construct_model(r) for r in request]

    async def count(self):
        db_request = {
            'table_name': self.model.table_name,
            'action': 'db__count',
        }

        return await self.db_manager.request(db_request)

    async def get(self, **kwargs):
        data = await self.filter(**kwargs)
        length = len(data)
        if length:
            if length > 1:
                raise QuerysetError(
                    'More than one {} where returned, there are {}!'.format(
                        self.model.__name__,
                        length,
                    )
                )

            return data[0]
        raise QuerysetError(
            'That {} does not exist'.format(self.model.__name__)
        )

    def calc_filters(self, kwargs, exclude=False):
        # recompose the filters
        bool_string = exclude and 'NOT ' or ''
        filters = []
        for k, v in kwargs.items():
            # we format the key, the conditional and the value
            middle = '='
            if len(k.split('__')) > 1:
                k, middle = k.split('__')
                middle = MIDDLE_OPERATOR[middle]

            field = getattr(self.model, k)

            if middle == '=' and isinstance(v, tuple):
                if len(v) != 2:
                    raise QuerysetError(
                        'Not a correct tuple definition, filter '
                        'only allows tuples of size 2'
                    )
                filters.append(
                    bool_string +
                    '({k}>{min} AND {k}<{max})'.format(
                        k=k,
                        min=field._sanitize_data(v[0]),
                        max=field._sanitize_data(v[1]),
                    )
                )
            else:
                v = field._sanitize_data(v)
                filters.append(bool_string + '{}{}{}'.format(k, middle, v))

        return filters

    async def filter(self, **kwargs):
        filters = self.calc_filters(kwargs)

        condition = ' AND '.join(filters)

        db_request = {
            'table_name': self.model.table_name,
            'action': 'db__select',
            'condition': condition
        }

        if self.model._ordering:
            db_request.update({'ordering': self.model._ordering})

        request = self.db_manager.request(db_request)
        return [self._construct_model(r) for r in await request]

    async def exclude(self, **kwargs):
        filters = self.calc_filters(kwargs, exclude=True)
        condition = ' AND '.join(filters)

        db_request = {
            'table_name': self.model.table_name,
            'action': 'db__select',
            'condition': condition
        }

        if self.model._ordering:
            db_request.update({'ordering': self.model._ordering})

        request = await self.db_manager.request(db_request)
        return [self._construct_model(r) for r in request]

    async def save(self, instanced_model):
        # performs the database save
        fields, field_data = [], []
        for k, data in instanced_model.data.items():
            f_class = getattr(instanced_model.__class__, k)

            field_name = f_class.field_name or k
            data = f_class._sanitize_data(data)

            fields.append(field_name)
            field_data.append(data)

        db_request = {
            'table_name': self.model.table_name,
            'action': (
                getattr(
                    instanced_model, instanced_model._orm_pk
                ) and 'db__update' or 'db__create'
            ),
            '_db_pk': instanced_model._db_pk,
            'model_id': getattr(
                instanced_model,
                instanced_model._orm_pk
            ),
            'field_names': ', '.join(fields),
            'field_values': ', '.join(field_data),
            'condition': '{}={}'.format(
                instanced_model._db_pk,
                getattr(instanced_model, instanced_model._orm_pk)
            )
        }
        try:
            response = await self.db_manager.request(db_request)
        except UniqueViolationError:
            raise ModelError('The model violates a unique constraint')

        self._construct_model(response, instanced_model)

    async def delete(self, instanced_model):
        db_request = {
            'table_name': self.model.table_name,
            'action': 'db__delete',
            'id_data': '{}={}'.format(
                instanced_model._db_pk,
                getattr(instanced_model, instanced_model._db_pk)
            )
        }
        response = await self.db_manager.request(db_request)
        return response


class ModelManager(Queryset):
    pass
