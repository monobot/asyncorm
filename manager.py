from database import Database_Manager
# import json

__all__ = ['ModelManager', ]

dm = Database_Manager()


class ModelManager(object):
    model = None

    async def _construct_object(self, data):
        obj = self.model()
        obj._construct(data)
        return obj

    async def _get_queryset(self):
        results = []
        for data in await dm.select(self._get_objects_query()):
            results.append(self.model()._construct(data))
        return results

    async def _get_filtered_queryset(self, **kwargs):
        results = []
        for data in await dm.select(self._get_objects_filtered(**kwargs)):
            results.append(self.model()._construct(data))
        return results

    def _get_objects_filtered(self, **kwargs):
        query = self._get_objects_query()
        condition = ','.join(['{}={}'.format(k, v) for k, v in kwargs.items()])

        query = query.replace(';',
            'WHERE ({}) ;'.format(condition)
        )
        return query

    def _get_objects_query(self):
        table_name = self.model.table_name
        return 'SELECT * FROM {table_name} ;'.format(table_name=table_name)

    @classmethod
    def queryset(cls):
        pass
