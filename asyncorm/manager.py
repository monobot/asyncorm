from asyncpg.exceptions import UniqueViolationError
from .fields import ManyToMany
from .exceptions import QuerysetError, ModelError
from .application import configure_orm, orm_app
__all__ = ['ModelManager', ]

dm = orm_app.db_manager

if not dm:
    orm = configure_orm({'db_config': {
            'database': 'asyncorm',
            'host': 'localhost',
            'user': 'sanicdbuser',
            'password': 'sanicDbPass',
        }})
    dm = orm.db_manager

MIDDLE_OPERATOR = {
    'gt': '>',
    'lt': '<',
    'gte': '>=',
    'lte': '<=',
}


class ModelManager(object):
    model = None

    @classmethod
    def _creation_query(cls):
        constraints = cls._get_field_constraints()
        unique_together = cls._get_unique_together()

        query = (
            'CREATE TABLE {table_name} ({field_queries}{unique_together});'
            '{constraints}{ending}'
        ).format(
            table_name=cls.model.table_name,
            field_queries=cls._get_field_queries(),
            unique_together=unique_together,
            constraints=constraints,
            ending=constraints and ';' or '',
        )
        # print(query)
        return query

    @classmethod
    def _get_field_queries(cls):
        # builds the table with all its fields definition
        return ', '.join(
            [f._creation_query() for f in cls.model.fields.values()
            if not isinstance(f, ManyToMany)]
        )

    @classmethod
    def _get_field_constraints(cls):
        # builds the table with all its fields definition
        return '; '.join(
            [f._field_constraints() for f in cls.model.fields.values()]
        )

    @classmethod
    def _get_unique_together(cls):
        # builds the table with all its fields definition
        unique_string = ', UNIQUE ({}) '.format(
            ','.join(cls.model._unique_together)
        )
        return cls.model._unique_together and unique_string or ''

    @classmethod
    def _get_m2m_field_queries(cls):
        # builds the relational 1_to_1 table
        return '; '.join(
            [f._creation_query() for f in cls.model.fields.values()
            if isinstance(f, ManyToMany)]
        )

    @classmethod
    def _construct_model(cls, record, instance=None):
        if not instance:
            instance = cls.model()

        data = {}
        for k, v in record.items():
            data.update({k: v})

        instance._construct(data)
        return instance

    @classmethod
    async def queryset(cls):
        return await cls.all()

    @classmethod
    async def all(cls):
        db_request = {
            'table_name': cls.model.table_name,
            'action': 'db__select_all',
        }

        return [cls._construct_model(r) for r in await dm.request(db_request)]

    @classmethod
    async def count(cls):
        db_request = {
            'table_name': cls.model.table_name,
            'action': 'db__count',
        }

        return await dm.request(db_request)

    @classmethod
    async def get(cls, **kwargs):
        data = await cls.filter(**kwargs)
        length = len(data)
        if length:
            if length > 1:
                raise QuerysetError(
                    'More than one {} where returned, there are {}!'.format(
                        cls.model.__name__,
                        length,
                    )
                )

            return data[0]
        raise QuerysetError(
            'That {} does not exist'.format(cls.model.__name__)
        )

    @staticmethod
    def calc_filters(model, kwargs, exclude=False):
        # recompose the filters
        bool_string = exclude and 'NOT ' or ''
        filters = []
        for k, v in kwargs.items():
            # we format the key, the conditional and the value
            middle = '='
            if len(k.split('__')) > 1:
                k, middle = k.split('__')
                middle = MIDDLE_OPERATOR[middle]

            field = getattr(model, k)

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

    @classmethod
    async def filter(cls, **kwargs):
        filters = cls.calc_filters(cls.model, kwargs)

        condition = ' AND '.join(filters)

        db_request = {
            'table_name': cls.model.table_name,
            'action': 'db__select',
            'condition': condition
        }

        if cls.model._ordering:
            db_request.update({'ordering': cls.model._ordering})
        return [cls._construct_model(r) for r in await dm.request(db_request)]

    @classmethod
    async def exclude(cls, **kwargs):
        filters = cls.calc_filters(cls.model, kwargs, exclude=True)
        condition = ' AND '.join(filters)

        db_request = {
            'table_name': cls.model.table_name,
            'action': 'db__select',
            'condition': condition
        }

        if cls.model._ordering:
            db_request.update({'ordering': cls.model._ordering})
        return [cls._construct_model(r) for r in await dm.request(db_request)]

    @classmethod
    async def save(cls, instanced_model):
        # performs the database save
        fields, field_data = [], []
        for k, data in instanced_model.data.items():
            f_class = getattr(instanced_model.__class__, k)

            field_name = f_class.field_name or k
            data = f_class._sanitize_data(data)

            fields.append(field_name)
            field_data.append(data)

        db_request = {
            'table_name': cls.model.table_name,
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
            response = await dm.request(db_request)
        except UniqueViolationError:
            raise ModelError('The model violates a unique constraint')

        cls._construct_model(response, instanced_model)

    @classmethod
    async def delete(cls, instanced_model):
        db_request = {
            'table_name': cls.model.table_name,
            'action': 'db__delete',
            'id_data': '{}={}'.format(
                instanced_model._db_pk,
                getattr(instanced_model, instanced_model._db_pk)
            )
        }
        response = await dm.request(db_request)
        return response
