from asyncorm.log import logger
import asyncpg


class GeneralManager(object):
    @property
    def db__create_table(self):
        return "CREATE TABLE IF NOT EXISTS {table_name} ({field_queries}) "

    @property
    def db__drop_table(self):
        return "DROP TABLE IF EXISTS {table_name} CASCADE"

    @property
    def db__alter_table(self):
        return "ALTER TABLE {table_name} ({field_queries}) "

    @property
    def db__constrain_table(self):
        return "ALTER TABLE {table_name} ADD {constrain} "

    @property
    def db__table_add_column(self):
        return "ALTER TABLE {table_name} ADD COLUMN {field_creation_string} "

    @property
    def db__table_alter_column(self):
        return self.db__table_add_column.replace("ADD COLUMN ", "ALTER COLUMN ")

    @property
    def db__insert(self):
        return "INSERT INTO {table_name} ({field_names}) VALUES ({field_schema}) RETURNING * "

    @property
    def db__select_all(self):
        return "SELECT {select} FROM {table_name} {join} {ordering}"

    @property
    def db__select_related(self):
        # LEFT JOIN inventory ON inventory.film_id = film.film_id;
        return (
            "LEFT JOIN {right_table} ON {foreign_field} = {right_table}.{model_db_pk} "
        )

    @property
    def db__select(self):
        return self.db__select_all.replace(
            "{ordering}", "WHERE ( {condition} ) {ordering}"
        )

    @property
    def db__exists(self):
        return "SELECT EXISTS({})".format(self.db__select)

    @property
    def db__where(self):
        """chainable"""
        return "WHERE {condition} "

    @property
    def db__select_m2m(self):
        return """
            SELECT {select} FROM {other_tablename}
            WHERE {otherdb_pk} = ANY (
                SELECT {other_tablename} FROM {m2m_tablename} WHERE {id_data}
            )
        """

    @property
    def db__update(self):
        return """
            UPDATE ONLY {table_name}
            SET ({field_names}) = ({field_schema})
            WHERE {id_data}
            RETURNING *
        """

    @property
    def db__delete(self):
        return "DELETE FROM {table_name} WHERE {id_data} "

    @property
    def db__create_field_index(self):
        return "CREATE INDEX {index_name} ON {table_name} ({colum_name}) "

    @staticmethod
    def query_clean(query):
        """Here we clean the queryset"""
        query += ";"
        return query

    @staticmethod
    def ordering_syntax(ordering):
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

    def construct_query(self, query_chain):
        # here we take the query_chain and convert to a real sql sentence
        res_dict = query_chain.pop(0)

        for q in query_chain:
            if q["action"] == "db__where":
                if res_dict["action"] == "db__select_all":
                    res_dict.update({"action": "db__select"})

                condition = res_dict.get("condition", "")
                if condition:
                    condition = " AND ".join([condition, q["condition"]])
                else:
                    condition = q["condition"]

                res_dict.update({"condition": condition})
            elif q["action"] == "db__select_related":
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
            res_dict["ordering"] = self.ordering_syntax(res_dict.get("ordering", []))
        else:
            res_dict["ordering"] = ""

        query = getattr(self, res_dict["action"]).format(**res_dict)
        query = self.query_clean(query)

        logger.debug(
            "QUERY: {}, VALUES: {}".format(query, res_dict.get("field_values"))
        )
        return query, res_dict.get("field_values")


class PostgresManager(GeneralManager):
    def __init__(self, conn_data):
        self._conn_data = conn_data
        self._conn = None

    async def get_conn(self):

        if not self._conn:
            pool = await asyncpg.create_pool(**self._conn_data)
            self._conn = await pool.acquire()
        return self._conn

    async def request(self, query):
        conn = await self.get_conn()

        async with conn.transaction():
            if isinstance(query, (tuple, list)):
                if query[1]:
                    return await conn.fetchrow(query[0], *query[1])
                else:
                    return await conn.fetchrow(query[0])
            return await conn.fetchrow(query)
