class GeneralManager(object):
    # things that belong to all the diff databases managers    @classmethod

    def __init__(self, conn_data):
        self.conn_data = conn_data
        self.conn = None


class PostgresManager(GeneralManager):

    @property
    def db__create_table(self):
        return '''
            CREATE TABLE IF NOT EXISTS {table_name}
            ({field_queries})'''

    @property
    def db__alter_table(self):
        return '''
            ALTER TABLE {table_name} ({field_queries})'''

    @property
    def db__constrain_table(self):
        return '''
            ALTER TABLE {table_name} ADD {constrain}'''

    @property
    def db__table_add_column(self):
        return '''
            ALTER TABLE {table_name}
            ADD COLUMN {field_creation_string}'''

    @property
    def db__table_alter_column(self):
        return self.db__table_add_column.replace(
            'ADD COLUMN ', 'ALTER COLUMN '
        )
    # @property
    # def db__count(self):
    #     return 'SELECT COUNT(*) FROM {table_name}'

    @property
    def db_insert(self):
        return '''
            INSERT INTO {table_name} ({field_names}) VALUES ({field_values})
            RETURNING *'''

    @property
    def db__select_all(self):
        return 'SELECT {select} FROM {table_name}'

    @property
    def db__select(self):
        return 'SELECT {select} FROM {table_name} WHERE {condition} '

    @property
    def db__select_m2m(self):
        return '''
            SELECT {select} FROM {other_tablename}
            WHERE {other_db_pk} = ANY (
                SELECT {other_tablename} FROM {m2m_tablename} WHERE {id_data}
            )'''

    @property
    def db__update(self):
        return '''
            UPDATE ONLY {table_name}
            SET ({field_names}) = ({field_values})
            WHERE {id_data}
            RETURNING *'''

    @property
    def db__delete(self):
        return 'DELETE FROM {table_name} WHERE {id_data}'

    async def get_conn(self):
        import asyncpg
        if not self.conn:
            pool = await asyncpg.create_pool(**self.conn_data)
            self.conn = await pool.acquire()
        return self.conn

    def query_clean(self, query):
        '''Here we clean the queryset'''
        if query[-1] != ';':
            query += ';'
        while '; ;' in query:
            query.replace('; ;', ';')
        while ';;' in query:
            query.replace(';;', ';')
        return query

    async def request(self, request_dict):
        query = getattr(self, request_dict['action']).format(**request_dict)
        query = self.query_clean(query)

        conn = await self.get_conn()

        if request_dict.get('ordering', None):
            query = query.replace(
                ';',
                'ORDER BY {};'.format(','.join(request_dict['ordering']))
            )

        # if request_dict['action'] == 'db__create_table':
        #     print(query)

        no_result = ['db__delete', 'db__create_table', 'db__alter_table',
                     'db__constrain_table', 'db__table_add_column',
                     'db__table_alter_column',
                     ]
        async with conn.transaction():
            result = await conn.fetch(query)
            if '__select' not in request_dict['action']:
                if request_dict['action'] not in no_result:
                    return result[0]
                return None
            else:
                return result

    async def transaction_insert(self, queries):
        conn = await self.get_conn()
        async with conn.transaction():
            for query in queries:
                await conn.execute(query)
