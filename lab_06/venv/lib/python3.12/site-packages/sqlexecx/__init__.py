"""
Examples
--------
>>> import sqlexecx as db
>>> db.init('db.sqlite3', driver='sqlite3', show_sql=True, debug=True)
Engine.SQLITE
>>> sql = 'insert into person(name, age) values(%s, %s)'
>>> db.execute(sql, '张三', 20)
1
>>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s'
>>> db.select(sql, '张三', 20)
[(3, '张三', 20)]
>>> db.select_one(sql, '张三', 20)
(3, '张三', 20)
>>> db.query(sql, '张三', 20)
[{'id': 3, 'name': '张三', 'age': 20}]
>>> db.query_one(sql, '张三', 20)
{'id': 3, 'name': '张三', 'age': 20}
>>> sql = 'SELECT count(1) FROM person WHERE name=%s and age=%s LIMIT 1'
>>> db.get(sql, '张三', 20)
1
"""

from sqlexecutorx import (
    conn,
    trans,
    get_connection,
    close,
    Driver,
    Engine,
    InitArgs,
    init as _init
)
from .exec import (
    execute,
    insert,
    save,
    save_sql,
    save_select_key,
    save_sql_select_key,
    batch_insert,
    batch_execute,
    get,
    select,
    select_one,
    select_first,
    query,
    query_one,
    query_first,
    ravel_list,
    select_page,
    query_page,
    load,
    do_execute,
    do_save_sql,
    do_save_sql_select_key,
    do_get,
    do_select,
    do_select_one,
    do_select_first,
    do_query,
    do_query_one,
    do_query_first,
    do_ravel_list,
    do_select_page,
    do_query_page,
    do_load,
    insert_from_df,
    insert_from_pl,
    insert_from_csv,
    insert_from_json,
    truncate_table,
    drop_table,
    show_tables
)

from .sql_exec import sql
from .page_exec import page
from .dialect import Dialect
from .table_exec import table


def init(*args, **kwargs) -> Engine:
    """
    Compliant with the Python DB API 2.0 (PEP-249).

    Addition parameters:
    :param driver=None: str|Driver, import driver, 'import pymysql'
    :param pool_size=0: int, default 0, size of connection pool
    :param show_sql=False: bool,  if True, print sql
    :param debug=False: bool, if True, print debug context

    Other parameters of connection pool refer to DBUtils: https://webwareforpython.github.io/DBUtils/main.html#pooleddb-pooled-db

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.init('db.sqlite3', driver='sqlite3', debug=True)
    >>> or
    >>> db.init("postgres://user:password@127.0.0.1:5432/testdb", driver='psycopg2', pool_size=5, debug=True)
    >>> or
    >>> db.init(user='root', password='xxx', host='127.0.0.1', port=3306, database='testdb', driver='pymysql')
    """

    engine = _init(*args, **kwargs)
    Dialect.init(engine)
    return engine
