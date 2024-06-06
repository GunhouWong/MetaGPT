import sqlparse
from dbutils.pooled_db import PooledDB


class DbUtil:
    def __init__(self, creator, **db_config):

        self.__pool = PooledDB(creator, **db_config)

    def select(self, sql, param=None):
        result = []
        with self.__pool.connection() as conn:
            with conn.cursor() as cursor:
                if param is None:
                    cursor.execute(sql)
                else:
                    cursor.execute(sql, param)

                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                for row in rows:
                    row_dict = {}
                    for i in range(len(columns)):
                        row_dict[columns[i]] = row[i]
                    result.append(row_dict)
        return result
