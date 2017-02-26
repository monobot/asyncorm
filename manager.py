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

    def _db_save(self, instanced_model, save_data):
        # this method is intended to make it more high level so isolate from
        # an specific database idiom
        pass

    def _create_save_string(self, instanced_model, fields, field_data):
        interpolate = ','.join(['{}'] * len(fields))
        save_string = '''
            INSERT INTO {table_name} ({interpolate}) VALUES ({interpolate});
        '''.format(
            table_name=instanced_model.__class__.table_name,
            interpolate=interpolate,
        )
        save_string = save_string.format(*tuple(fields + field_data))
        return save_string

    def _update_save_string(self, instanced_model, fields, field_data):
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

    def _get_objects_filtered(self, **kwargs):
        query = self._get_objects_query()
        filter_list = []

        for k, v in kwargs.items():
            # we format the key, the conditional and the value
            middle = '='
            if len(k.split('__')) > 1:
                k, middle = k.split('__')
                middle = MIDDLE_OPERATOR[middle]

            field = getattr(self.model, k)
            v = field._sanitize_data(v)

            filter_list.append('{}{}{}'.format(k, middle, v))

        condition = ' AND '.join(filter_list)
        query = query.replace(';',
            'WHERE {} ;'.format(condition)
        )
        return query


class ModelManager(ModelDbManager):
    model = None

    def _get_objects_query(self):
        table_name = self.model.table_name
        return 'SELECT * FROM {table_name} ;'.format(table_name=table_name)

    async def _get_queryset(self):
        results = []
        for data in await dm.select(self._get_objects_query()):
            results.append(self.model()._construct(data))
        return results

    async def get(self, **kwargs):
        data = await dm.select(self._get_objects_filtered(**kwargs))
        length = len(data)
        if length:
            if length > 1:
                raise QuerysetError(
                    'More than one {} where returned, there are {}!'.format(
                        self.model.__name__,
                        length,
                    )
                )

            construct = self.model()._construct(data[0])
        return construct

    async def filter(self, **kwargs):
        results = []
        for data in await dm.select(self._get_objects_filtered(**kwargs)):
            results.append(self.model()._construct(data))
        return results

    async def save(self, instanced_model):
        # performs the database save
        fields, field_data = [], []
        for k, data in instanced_model.data.items():
            f_class = getattr(instanced_model.__class__, k)

            # we add the field_name in db
            fields.append(f_class.field_name or k)
            field_data.append(f_class._sanitize_data(data))

        self._update_save_string(instanced_model, fields, field_data)
        if getattr(instanced_model, instanced_model._fk_db_fieldname):
            query = self._update_save_string(
                instanced_model,
                fields, field_data
            )
        query = self._create_save_string(instanced_model, fields, field_data)
        info_back = self._get_objects_filtered(**instanced_model.data)

        data = await dm.transaction_insert([query, info_back])
        # print(data)
        # print(data.__class__)
        # instanced_model._construct(**data)

    @classmethod
    def queryset(cls):
        pass
