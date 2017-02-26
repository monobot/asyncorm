from database import PostgresManager
from exceptions import QuerysetError
# import json

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


class ModelDbManager(object):

    @classmethod
    def _get_objects_query(cls):
        table_name = cls.model.table_name
        return 'SELECT * FROM {table_name} ;'.format(table_name=table_name)

    @classmethod
    def _get_objects_filtered(cls, **kwargs):
        query = cls._get_objects_query()
        filter_list = []

        for k, v in kwargs.items():
            # we format the key, the conditional and the value
            middle = '='
            if len(k.split('__')) > 1:
                k, middle = k.split('__')
                middle = MIDDLE_OPERATOR[middle]

            field = getattr(cls.model, k)
            v = field._sanitize_data(v)

            filter_list.append('{}{}{}'.format(k, middle, v))

        condition = ' AND '.join(filter_list)
        query = query.replace(';', 'WHERE {} ;'.format(condition))
        return query


class ModelManager(ModelDbManager):
    model = None

    @classmethod
    async def _get_queryset(cls):
        results = []
        for data in await dm.select(cls._get_objects_query()):
            results.append(cls.model()._construct(data))
        return results

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

            construct = cls.model()._construct(data[0])
            return construct
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
        response = await dm._request(db_request)
        return response

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
        response = await dm._request(db_request)

        data = {}
        for k, v in response.items():
            data.update({k: v})
        instanced_model._construct(data)

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
        response = await dm._request(db_request)
        return response

    @classmethod
    async def queryset(cls):
        return await cls.all()

    @classmethod
    async def all(cls):

        db_request = {
            'table_name': cls.model.table_name,
            'action': '_object__select_all',
        }
        response = await dm._request(db_request)
        return response
