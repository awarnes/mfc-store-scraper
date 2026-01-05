import json
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv(dotenv_path="./.env.local")


def adapt_dict(dict_var):
    return psycopg2.extensions.AsIs("'" + json.dumps(dict_var) + "'")


class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            host=os.getenv("DB_HOST"),
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
                with open("./base_schema.sql", "r") as schema:
                    curs.execute(schema.read())

    def batch_execute(self, sql, data):
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.executemany(sql, data)


if __name__ == "__main__":
    database = Database()

    database.setup_database()
