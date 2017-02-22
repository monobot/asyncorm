from database import Database_Manager
import json

__all__ = ['ModelManager', ]

dm = Database_Manager()


class ModelManager(object):
    model = None

    async def _get_queryset(self, **kwargs):
        result = json.decode(await dm.select(self._get_objects_query()))
        print(result)

    def _get_objects_query(self):
        table_name = self.model.table_name
        return 'SELECT * FROM {table_name} ;'.format(
            table_name=table_name,
        )

    @classmethod
    def queryset(cls):
        pass
