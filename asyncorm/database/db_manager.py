import asyncpg

from asyncorm.database.db_cursor import Cursor
from asyncorm.log import logger


class GeneralManager(object):
    @property
    def _db__create_table(self):
        return "CREATE TABLE IF NOT EXISTS {table_name} ({field_queries}) "

    @property
    def _db__drop_table(self):
        return "DROP TABLE IF EXISTS {table_name} CASCADE"

    @property
    def _db__alter_table(self):
        return "ALTER TABLE {table_name} ({field_queries}) "

    @property
    def _db__constrain_table(self):
        return "ALTER TABLE {table_name} ADD {constrain} "

    @property
    def db__table_add_column(self):
        return "ALTER TABLE {table_name} ADD COLUMN {field_creation_string} "

    @property
    def _db__table_alter_column(self):
        return self.db__table_add_column.replace("ADD COLUMN ", "ALTER COLUMN ")

    @property
    def _db__insert(self):
        return "INSERT INTO {table_name} ({field_names}) VALUES ({field_schema}) RETURNING * "

    @property
    def _db__select_all(self):
        return "SELECT {select} FROM {table_name} {join} {ordering}"

    @property
    def _db__select_related(self):
        # LEFT JOIN inventory ON inventory.film_id = film.film_id;
        return (
            "LEFT JOIN {right_table} ON {foreign_field} = {right_table}.{model_db_pk} "
        )

    @property
    def _db__select(self):
        return self._db__select_all.replace(
            "{ordering}", "WHERE ( {condition} ) {ordering}"
        )

    @property
    def _db__exists(self):
        return "SELECT EXISTS({})".format(self._db__select)

    @property
    def _db__where(self):
        """chainable"""
        return "WHERE {condition} "

    @property
    def _db__select_m2m(self):
        return """
            SELECT {select} FROM {other_tablename}
            WHERE {otherdb_pk} = ANY (
                SELECT {other_tablename} FROM {m2m_tablename} WHERE {id_data}
            )
        """

    @property
    def _db__update(self):
        return """
            UPDATE ONLY {table_name}
            SET ({field_names}) = ({field_schema})
            WHERE {id_data}
            RETURNING *
        """

    @property
    def _db__delete(self):
        return "DELETE FROM {table_name} WHERE {id_data} "

    @property
    def _db__create_field_index(self):
        return "CREATE INDEX {index_name} ON {table_name} ({colum_name}) "

    @staticmethod
    def _query_clean(query):
        """Here we clean the queryset"""
        query += ";"
        return query

    @staticmethod
    def _ordering_syntax(ordering):
        result = []
        if not ordering:
            return ""
        for f in ordering:
            if f.startswith("-"):
                result.append(" {} DESC ".format(f[1:]))
            else:
                result.append(f)
        result = "ORDER BY {}".format(",".join(result))
        return result

    def _construct_query(self, query_chain):
        # here we take the query_chain and convert to a real sql sentence
        res_dict = query_chain.pop(0)

        for q in query_chain:
            if q["action"] == "_db__where":
                if res_dict["action"] == "_db__select_all":
                    res_dict.update({"action": "_db__select"})

                condition = res_dict.get("condition", "")
                if condition:
                    condition = " AND ".join([condition, q["condition"]])
                else:
                    condition = q["condition"]

                res_dict.update({"condition": condition})
            elif q["action"] == "_db__select_related":
                for model_join in q["fields"]:
                    join_const = getattr(self, q["action"]).format(**model_join)
                    res_dict["join"] += join_const

                    select = res_dict["select"][:]

                    if select == "COUNT(*)":
                        pass
                    elif select == "*":
                        select = select.replace(
                            "*",
                            "{left_table}.*, {f_formatter}".format(
                                left_table=model_join["left_table"],
                                f_formatter=model_join["fields_formatter"],
                            ),
                        )
                        res_dict["select"] = select
                    else:
                        res_dict["select"] += ", " + model_join["fields_formatter"]

        # if we are not counting, then we can assign ordering
        operations = ["COUNT", "MAX", "MIN", "SUM", "AVG", "STDDEV"]
        if res_dict.get("select", "").split("(")[0] not in operations:
            res_dict["ordering"] = self._ordering_syntax(res_dict.get("ordering", []))
        else:
            res_dict["ordering"] = ""

        query = getattr(self, res_dict["action"]).format(**res_dict)
        query = self._query_clean(query)

        logger.debug(
            "QUERY: {}, VALUES: {}".format(query, res_dict.get("field_values"))
        )
        return query, res_dict.get("field_values")


class PostgresManager(GeneralManager):
    def __init__(self, conn_data):
        self._conn_data = conn_data
        self._conn = None
        self._pool = None

    async def _get_pool(self):
        """Get a connections pool from the database.

        :return: connection pool
        :rtype: asyncpg pool
        """
        if self._pool is None:
            self._pool = await asyncpg.create_pool(**self._conn_data)
        return self._pool

    async def _get_connection(self):
        """Set a connection to the database.

        :return: Connection set
        :rtype: asyncpg.connection
        """
        if not self._conn:
            self._pool = await self._get_pool()
            self._conn = await self._pool.acquire()

        return self._conn

    async def get_cursor(self, query, forward, stop):
        await self._get_connection()
        query = self._construct_query(query)
        return Cursor(self._conn, query[0], values=query[1], forward=forward, stop=stop)

    async def request(self, query):
        """Send a database request inside a transaction.

        :param query: sql sentence
        :type query: str
        :return: asyncpg Record object
        :rtype: asyncpg.Record
        """
        await self._get_pool()

        conn = await self._get_connection()
        async with conn.transaction():
            if isinstance(query, (tuple, list)):
                if query[1]:
                    return await conn.fetchrow(query[0], *query[1])
                else:
                    return await conn.fetchrow(query[0])
            return await conn.fetchrow(query)
        self._conn = await self._pool.acquire()
