from sqlexecx import (
    conn,
    trans,
    get_connection,
    close,
    Driver,
    Dialect,
    Engine,
    init as _init
)

from .support import InitArgs
from .sql_mapper import sql, mapper


def init_db(*args, **kwargs):
    """
    Compliant with the Python DB API 2.0 (PEP-249).

    from mysqlx import init_db
    init_db('test.db', driver='sqlite3', show_sql=True, debug=True)
    or
    init_db("postgres://user:password@127.0.0.1:5432/testdb", mapper_path='./mapper', driver='psycopg2', pool_size=5, show_sql=True, debug=True)
    or
    init_db(user='root', password='xxx', host='127.0.0.1', port=3306, database='testdb', mapper_path='./mapper', driver='pymysql', pool_size=5, show_sql=True, debug=True)

    Addition parameters:
    :param mapper_path: str, path of mapper files
    :param driver=None: str, import driver, 'import pymysql'
    :param pool_size=0: int, default 0, size of connection pool
    :param show_sql=False: bool,  if True, print sql
    :param debug=False: bool, if True, print debug context

    Other parameters of connection pool refer to DBUtils: https://webwareforpython.github.io/DBUtils/main.html#pooleddb-pooled-db
    """
    from .sql_holder import load_mapper

    # Dialect.init(Engine.MYSQL)
    mapper_path = kwargs.pop(InitArgs.MAPPER_PATH) if InitArgs.MAPPER_PATH in kwargs else None
    _init(*args, **kwargs)
    if mapper_path:
        load_mapper(mapper_path)
