from database import Database_Manager
# import json

__all__ = ['ModelManager', ]

dm = Database_Manager()


class ModelManager(object):
    model = None

    async def build_object(self, data):
        obj = self.model()
        obj.build(data)
        return obj

    async def _get_queryset(self, **kwargs):
        results = []
        for data in await dm.select(self._get_objects_query()):
            results.append(self.model().build(data))
        return results

    def _get_objects_query(self):
        table_name = self.model.table_name
        return 'SELECT * FROM {table_name} ;'.format(table_name=table_name)

    @classmethod
    def queryset(cls):
        pass
