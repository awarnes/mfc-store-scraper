import json

import psycopg2

from src.azure.settings import settings


def adapt_dict(dict_var):
    return psycopg2.extensions.AsIs("'" + json.dumps(dict_var) + "'")


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=settings.db_name,
            user=settings.db_username,
            password=settings.db_password,
            port=settings.db_port,
            host=settings.db_host,
        )

        psycopg2.extensions.register_adapter(dict, adapt_dict)

    def fetchall(self, query):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute(query)
                return curs.fetchall()

    def close(self):
        return self.conn.close()

    def setup_database(self):
        with self.conn as conn:
            with conn.cursor() as curs:
                with open("./src/azure/base_schema.sql", "r") as schema:
                    curs.execute(schema.read())

    def batch_execute(self, sql, data):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.executemany(sql, data)


if __name__ == "__main__":
    database = Database()

    database.setup_database()
