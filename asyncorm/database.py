class GeneralManager(object):
    # things that belong to all the diff databases managers    @classmethod

    def __init__(self, conn_data):
        self.conn_data = conn_data
        self.conn = None


class PostgresManager(GeneralManager):

    @property
    def db__create(self):
        return '''
            INSERT INTO {table_name} ({field_names}) VALUES ({field_values})
            RETURNING * ;
        '''

    @property
    def db__count(self):
        return 'SELECT COUNT(*) FROM {table_name} ;'

    @property
    def db__select_all(self):
        return 'SELECT * FROM {table_name} ;'

    @property
    def db__select(self):
        return 'SELECT * FROM {table_name} WHERE {condition} ;'

    @property
    def db__update(self):
        return '''
            UPDATE ONLY {table_name}
            SET ({field_names}) = ({field_values})
            WHERE {_db_pk}={model_id}
            RETURNING * ;
        '''

    @property
    def db__delete(self):
        return 'DELETE FROM {table_name} WHERE {id_data} ;'

    async def get_conn(self):
        import asyncpg
        if not self.conn:
            pool = await asyncpg.create_pool(**self.conn_data)
            self.conn = await pool.acquire()
        return self.conn

    async def request(self, request_dict):
        query = getattr(self, request_dict['action']).format(**request_dict)
        conn = await self.get_conn()

        if request_dict.get('ordering', None):
            query = query.replace(
                ';', 'ORDER BY {};'.format(','.join(request_dict['ordering']))
            )

        # print(query)
        async with conn.transaction():
            result = await conn.fetch(query)
            if '__select' not in request_dict['action']:
                if request_dict['action'] != 'db__delete':
                    return result[0]
                else:
                    return None
            else:
                return result

    async def transaction_insert(self, queries):
        conn = await self.get_conn()
        async with conn.transaction():
            for query in queries:
                print(query)
                await conn.execute(query)
