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
    def _db_save(cls, instanced_model, save_data):
        # this method is intended to make it more high level so isolate from
        # an specific database idiom
        pass

    @classmethod
    def _create_save_string(cls, instanced_model, fields, field_data):
        interpolate = ','.join(['{}'] * len(fields))
        save_string = '''
            INSERT INTO {table_name} ({interpolate}) VALUES ({interpolate});
        '''.format(
            table_name=instanced_model.__class__.table_name,
            interpolate=interpolate,
        )
        save_string = save_string.format(*tuple(fields + field_data))
        return save_string

    @classmethod
    def _delete_string(cls, instanced_model):
        id_data = '{}={}'.format(
            instanced_model._fk_db_fieldname,
            getattr(instanced_model, instanced_model._fk_db_fieldname)
        )
        delete_string = '''
            DELETE FROM {table_name} WHERE {id_data};
        '''.format(
            table_name=instanced_model.__class__.table_name,
            id_data=id_data,
        )
        return delete_string

    @classmethod
    def _update_save_string(cls, instanced_model, fields, field_data):
        interpolate = ','.join(['{}'] * len(fields))
        save_string = '''
            UPDATE ONLY {table_name} SET ({interpolate}) VALUES ({interpolate})
            WHERE {_fk_db_fieldname}={model_id};
        '''.format(
            table_name=instanced_model.__class__.table_name,
            interpolate=interpolate,
            _fk_db_fieldname=instanced_model._fk_db_fieldname,
            model_id=getattr(
                instanced_model,
                instanced_model._fk_orm_fieldname
            )
        )
        save_string = save_string.format(*tuple(fields + field_data))
        return save_string

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
        query = query.replace(';',
            'WHERE {} ;'.format(condition)
        )
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
        data = await dm.select(cls._get_objects_filtered(**kwargs))
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
        results = []
        for data in await dm.select(cls._get_objects_filtered(**kwargs)):
            results.append(cls.model()._construct(data))
        return results

    @classmethod
    async def save(cls, instanced_model):
        # performs the database save
        fields, field_data = [], []
        for k, data in instanced_model.data.items():
            f_class = getattr(instanced_model.__class__, k)

            # we add the field_name in db
            fields.append(f_class.field_name or k)
            field_data.append(f_class._sanitize_data(data))

        cls._update_save_string(instanced_model, fields, field_data)
        if getattr(instanced_model, instanced_model._fk_db_fieldname):
            query = cls._update_save_string(
                instanced_model,
                fields, field_data
            )
        query = cls._create_save_string(instanced_model, fields, field_data)
        info_back = cls._get_objects_filtered(**instanced_model.data)

        result_object = await dm._save([query, info_back])

        data = {}
        for k, v in result_object.items():
            data.update({k: v})
        instanced_model._construct(data)

    @classmethod
    async def delete(cls, instanced_model):
        # performs the database delete
        query = cls._delete_string(instanced_model)
        await dm._delete(query)

        return None

    @classmethod
    def queryset(cls):
        pass

    @classmethod
    async def all(cls):
        results = []
        for data in await dm.select(cls._get_objects_query()):
            results.append(cls.model()._construct(data))
        return results
