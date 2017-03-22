from asyncpg.exceptions import UniqueViolationError

from .exceptions import QuerysetError, ModelError
from .fields import ManyToMany, ForeignKey  # , ManyToMany
# from .log import logger

__all__ = ['FieldQueryset', 'ModelManager', 'Queryset']

MIDDLE_OPERATOR = {
    'gt': '>',
    'lt': '<',
    'gte': '>=',
    'lte': '<=',
}


# this is a decorator for future lazy queryset
def queryset_checker(func):
    def checker(self, *args, **kargs):
        return func(self, *args, **kargs)
    return checker


class Queryset(object):
    db_manager = None
    orm = None

    def __init__(self, model):
        self.model = model

        self.table_name = self.model.table_name()
        self.select = '*'

        self.query_chain = []

    @classmethod
    def _set_orm(cls, orm):
        cls.orm = orm
        cls.db_manager = orm.db_manager

    # def _copy_me(self):
    #     queryset = Queryset()
    #     queryset.model = self.model
    #     return queryset

    def _get_field_queries(self):
        # Builds the creationquery for each of the non fk or m2m fields
        return ', '.join(
            [f._creation_query() for f in self.model.fields.values()
             if not isinstance(f, ManyToMany) and
             not isinstance(f, ForeignKey)
             ]
        )

    async def _create_table(self):
        '''
        Builds the table without the m2m_fields and fks
        '''
        db_request = {
            'table_name': self.model.table_name(),
            'action': 'db__create_table',
            'field_queries': self._get_field_queries(),
        }

        await self.db_request(db_request)

    async def _unique_together(self):
        '''
        Builds the unique together constraint
        '''
        unique_together = self._get_unique_together()

        if unique_together:
            db_request = {
                'table_name': self.model.table_name(),
                'action': 'db__constrain_table',
                'constrain': unique_together,
            }

            await self.db_request(db_request)

    async def _add_fk_columns(self):
        '''
        Builds the fk fields
        '''
        for n, f in self.model.fields.items():
            if isinstance(f, ForeignKey):

                db_request = {
                    'table_name': self.model.table_name(),
                    'action': 'db__table_add_column',
                    'field_creation_string': f._creation_query(),
                }

                await self.db_request(db_request)

    async def _add_m2m_columns(self):
        '''
        Builds the m2m_fields
        '''
        for n, f in self.model.fields.items():
            if isinstance(f, ManyToMany):

                db_request = {
                    'table_name': f.table_name,
                    'action': 'db__create_table',
                    'field_queries': f._creation_query(),
                }

                await self.db_request(db_request)

    def _get_unique_together(self):
        # builds the table with all its fields definition
        unique_string = ' UNIQUE ({}) '.format(
            ','.join(self.model.unique_together)
        )
        return self.model.unique_together and unique_string or ''

    def _model_constructor(self, record, instance=None):
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
        db_request = {'action': 'db__select_all'}

        request = await self.db_request(db_request)
        return [self._model_constructor(r) for r in request]

    async def count(self):
        self.select = 'COUNT(*)'
        db_request = {'action': 'db__count'}

        return await self.db_request(db_request)

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

        # if the queryset is a real model_queryset
        if self.model:
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

        else:
            for k, v in kwargs.items():
                filters.append('{}={}'.format(k, v))
        return filters

    async def filter(self, **kwargs):
        filters = self.calc_filters(kwargs)

        condition = ' AND '.join(filters)

        db_request = {'action': 'db__select', 'condition': condition}

        if self.model.ordering:
            db_request.update({'ordering': self.model.ordering})

        request = self.db_request(db_request)
        return [self._model_constructor(r) for r in await request]

    async def filter_m2m(self, m2m_filter):
        m2m_filter.update({'action': 'db__select_m2m'})
        if self.model.ordering:
            m2m_filter.update({'ordering': self.model.ordering})

        results = await self.db_request(m2m_filter)
        if results.__class__.__name__ == 'Record':
            results = [results, ]

        return [self._model_constructor(r) for r in results]

    async def exclude(self, **kwargs):
        filters = self.calc_filters(kwargs, exclude=True)
        condition = ' AND '.join(filters)

        db_request = {'action': 'db__select', 'condition': condition}

        if self.model.ordering:
            db_request.update({'ordering': self.model.ordering})

        request = await self.db_request(db_request)
        return [self._model_constructor(r) for r in request]

    async def db_request(self, db_request):
        db_request.update({
            'select': db_request.get('select', self.select),
            'table_name': db_request.get(
                'table_name', self.model.table_name()
            ),
        })
        response = await self.db_manager.request(db_request)
        return response


class FieldQueryset(Queryset):

    def __init__(self, field, *args):
        self.field = field
        super().__init__(*args)


class ModelManager(Queryset):

    def __init__(self, model):
        self.model = model
        super().__init__(model)

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
            'action': (
                getattr(
                    instanced_model, instanced_model._orm_pk
                ) and 'db__update' or 'db_insert'
            ),
            'id_data': '{}={}'.format(
                instanced_model._db_pk,
                getattr(instanced_model, instanced_model._orm_pk),
            ),
            'field_names': ', '.join(fields),
            'field_values': ', '.join(field_data),
            'condition': '{}={}'.format(
                instanced_model._db_pk,
                getattr(instanced_model, instanced_model._orm_pk)
            )
        }
        try:
            response = await self.db_request(db_request)
        except UniqueViolationError:
            raise ModelError('The model violates a unique constraint')

        self._model_constructor(response, instanced_model)

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

            model_column = instanced_model.table_name()

            model_id = getattr(instanced_model, instanced_model._orm_pk)

            db_request = {
                'table_name': table_name,
                'action': 'db_insert',
                'field_names': ', '.join([model_column, foreign_column]),
                'field_values': ', '.join([str(model_id), str(data)]),
                # 'ordering': 'id',
            }

            if isinstance(data, list):
                for d in data:
                    db_request.update(
                        {'field_values': ', '.join([str(model_id), str(d)])}
                    )
                    await self.db_request(db_request)
            else:
                await self.db_request(db_request)

    async def delete(self, instanced_model):
        db_request = {
            'action': 'db__delete',
            'id_data': '{}={}'.format(
                instanced_model._db_pk,
                getattr(instanced_model, instanced_model._db_pk)
            )
        }
        return await self.db_request(db_request)
