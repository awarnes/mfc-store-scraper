"""Connection helper for the PostgreSQL database"""
import json

import psycopg2

from src.settings import settings

def adapt_dict(dict_var):
    """Helper to insert JSONB data into PostgreSQL database"""
    return psycopg2.extensions.AsIs("'" + json.dumps(dict_var) + "'")

class Database:
    """Connection helper for the PostgreSQL database"""

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
        """Helper to run a query and return all results"""
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.execute(query)
                return curs.fetchall()

    def close(self):
        """Helper to close the database connection"""
        return self.conn.close()

    def batch_execute(self, sql, data):
        """
        Helper to run multiple queries in a row
        NOTE: this is not efficient, at some point it may be worth
        updating to the better batch execute code
        """
        with self.conn as conn:
            with conn.cursor() as curs:
                curs.executemany(sql, data)
