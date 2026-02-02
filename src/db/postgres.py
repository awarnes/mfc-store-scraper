"""Connection helper for the PostgreSQL database"""

import psycopg

from src.settings import settings

class Database:
    """Connection helper for the PostgreSQL database"""

    def fetchall(self, query):
        """Helper to run a query and return all results"""
        with psycopg.connect(
            dbname=settings.db_name,
            user=settings.db_username,
            password=settings.db_password,
            port=settings.db_port,
            host=settings.db_host,
        ) as conn:
            with conn.cursor() as curs:
                curs.execute(query)
                return curs.fetchall()

    def batch_execute(self, sql, data):
        """
        Helper to run multiple queries in a row
        NOTE: this is not efficient, at some point it may be worth
        updating to the better batch execute code
        """
        with psycopg.connect(
            dbname=settings.db_name,
            user=settings.db_username,
            password=settings.db_password,
            port=settings.db_port,
            host=settings.db_host,
        ) as conn:
            with conn.cursor() as curs:
                curs.executemany(sql, data)
