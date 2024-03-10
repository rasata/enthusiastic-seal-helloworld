import os
import libsql_client
from libsql_client import ResultSet

DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASE_AUTH_TOKEN = os.environ.get("DATABASE_AUTH_TOKEN")


def format_result_set(result_set: ResultSet):
    return [dict(zip(result_set.columns, row)) for row in result_set.rows]


def db_execute(*args):
    with libsql_client.create_client_sync(
        DATABASE_URL, auth_token=DATABASE_AUTH_TOKEN
    ) as client:
        return client.execute(*args)
