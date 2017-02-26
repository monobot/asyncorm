from fields import ManyToMany
from database import PostgresManager
from exceptions import QuerysetError

__all__ = ['ModelManager', ]

dm = PostgresManager({
    'database': 'asyncorm',
    'host': 'localhost',
    'user': 'sanicdbuser',
    'password': 'sanicDbPass',
    # 'loop': loop,
})


MIDDLE_OPERATOR = {
    'gt': '>',
    'lt': '<',
    'gte': '>=',
    'lte': '>=',
}


class ModelManager(object):
    model = None

    @classmethod
    def _creation_query(cls):
        constraints = cls._get_field_constraints()

        query = (
            'CREATE TABLE {table_name} ({field_queries});{constraints}{ending}'
        ).format(
            table_name=cls.model.table_name,
            field_queries=cls._get_field_queries(),
            constraints=constraints,
            ending=constraints and ';' or '',
        )
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
            'action': '_object__select_all',
        }

        return [cls._construct_model(r) for r in await dm.request(db_request)]

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

    @classmethod
    async def filter(cls, **kwargs):
        filters = []
        for k, v in kwargs.items():
            # we format the key, the conditional and the value
            middle = '='
            if len(k.split('__')) > 1:
                k, middle = k.split('__')
                middle = MIDDLE_OPERATOR[middle]

            field = getattr(cls.model, k)
            v = field._sanitize_data(v)

            filters.append('{}{}{}'.format(k, middle, v))
        condition = ' AND '.join(filters)

        db_request = {
            'table_name': cls.model.table_name,
            'action': '_object__select',
            'condition': condition
        }

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
                    instanced_model, instanced_model._fk_db_fieldname
                ) and '_object__update' or '_object__create'
            ),
            '_fk_db_fieldname': instanced_model._fk_db_fieldname,
            'model_id': getattr(
                instanced_model,
                instanced_model._fk_orm_fieldname
            ),
            'field_names': ', '.join(fields),
            'field_values': ', '.join(field_data),
            'condition': '{}={}'.format(
                instanced_model._fk_db_fieldname,
                getattr(instanced_model, instanced_model._fk_db_fieldname)
            )
        }
        response = await dm.request(db_request)

        cls._construct_model(response, instanced_model)

    @classmethod
    async def delete(cls, instanced_model):
        db_request = {
            'table_name': cls.model.table_name,
            'action': '_object__delete',
            'id_data': '{}={}'.format(
                instanced_model._fk_db_fieldname,
                getattr(instanced_model, instanced_model._fk_db_fieldname)
            )
        }
        response = await dm.request(db_request)
        return response
