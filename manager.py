__all__ = ['ModelManager', ]


class ModelManager(object):
    model = None

    def _get_objects_query(self):
        table_name = self.model.table_name
        return 'SELECT * FROM {table_name} ;'.format(
            table_name=table_name,
        )

    @classmethod
    def queryset(cls):
        pass
