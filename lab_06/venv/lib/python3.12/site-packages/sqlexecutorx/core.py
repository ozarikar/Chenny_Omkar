# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List, Tuple, Any
from .log_support import logger
from .engine import Engine, Driver
from .constant import MODULE, LIMIT_1, LIMIT_2
from .init_import import import_driver
from .log_support import do_sql_log, do_save_log, batch_sql_log, page_log
from .sql_support import limit_sql, require_limit, is_tuple_or_list
from .support import DBCtx, try_commit, DB_LOCK, Dict, InitArgs
from .error import MultiRowsError, MultiColumnsError
from ._context import _NoParamDecoratorContextManager

_DB_CTX = None
_POOLED = False
_SHOW_SQL = False


def init(*args, **kwargs) -> Engine:
    """
    Compliant with the Python DB API 2.0 (PEP-249).

    Addition parameters:
    :param driver=None: str|Driver, 'psycopg2' or 'pymysql' or 'mysql.connector' or 'sqlite3'
    :param pool_size=0: int, default 0, size of connection pool
    :param show_sql=False: bool,  if True, print sql
    :param debug=False: bool, if True, print debug context

    Other parameters of connection pool refer to DBUtils: https://webwareforpython.github.io/DBUtils/main.html#pooleddb-pooled-db

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> db.init('db.sqlite3', driver='sqlite3', show_sql=True debug=True)
    >>> or
    >>> db.init("postgres://user:password@127.0.0.1:5432/testdb", driver='psycopg2', pool_size=5, debug=True)
    >>> or
    >>> db.init(user='root', password='xxx', host='127.0.0.1', port=3306, database='testdb', driver='pymysql')
    """

    global _DB_CTX
    global _SHOW_SQL
    
    if _DB_CTX is not None:
        logger.warn('Database is already initialized.')
        return None
    
    pool_size = 0
    pool_args = ['mincached', 'maxcached', 'maxshared', 'maxconnections', 'blocking', 'maxusage', 'setsession', 'reset',
                 'failures', 'ping']
    
    _SHOW_SQL = kwargs.pop(InitArgs.SHOW_SQL) if InitArgs.SHOW_SQL in kwargs else False
    driver = kwargs.pop(InitArgs.DRIVER) if InitArgs.DRIVER in kwargs else None
    engine, driver_name, creator = import_driver(driver, *args, **kwargs)
    prepared = Driver.MYSQL_CONNECTOR.value == driver_name
    if InitArgs.DEBUG in kwargs and kwargs.pop(InitArgs.DEBUG):
        from logging import DEBUG
        logger.setLevel(DEBUG)

    if InitArgs.POOL_SIZE in kwargs:
        # mysql.connector 用自带连接池
        pool_size = kwargs[InitArgs.POOL_SIZE] if prepared else kwargs.pop(InitArgs.POOL_SIZE)

    pool_kwargs = {key: kwargs.pop(key) for key in pool_args if key in kwargs}
    _connect = lambda: creator.connect(*args, **kwargs)
    if pool_size >= 1 and not prepared:
        from .pooling import pooled_connect
        global _POOLED
        _POOLED = True
        _connect = pooled_connect(_connect, pool_size, **pool_kwargs)

    with DB_LOCK:
        if _DB_CTX is None:
            _DB_CTX = DBCtx(connect=_connect, prepared=prepared)
            if pool_size > 0:
                logger.info(
                    "Inited database <%s> of %s with driver: '%s' and pool size: %d." % (hex(id(_DB_CTX)), engine.value,
                                                                                         driver_name, pool_size))
            else:
                logger.info(
                    "Inited database <%s> of %s with driver: '%s'." % (hex(id(_DB_CTX)), engine.value, driver_name))
        else:
            logger.warning('Database is already initialized.')

    return engine


class conn(_NoParamDecoratorContextManager):
    r"""Context-manager that connction.

    Example::
        >>> from sqlexecutorx import conn
        >>> @conn
        >>> def foo(*args, **kw):
        >>>     f1()
        >>>     f2()
        >>>
        >>> with conn():
        >>>     pass
    """

    def __init__(self):
        super().__init__()
        self.db_ctx = _DB_CTX

    def __enter__(self):
        self.should_cleanup = False
        if self.db_ctx.try_init():
            self.should_cleanup = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        if self.should_cleanup:
            self.db_ctx.release()


class trans(_NoParamDecoratorContextManager):
    r"""Context-manager that transaction.

    Example::
        >>> from sqlexecutorx import trans
        >>> @trans
        >>> def foo(*args, **kw):
        >>>     f1()
        >>>     f2()
        >>>
        >>> with trans():
        >>>     pass
    """

    def __init__(self):
        super().__init__()
        self.db_ctx = _DB_CTX

    def __enter__(self):
        self.should_close_conn = False
        if self.db_ctx.try_init():
            # needs open a connection first:
            self.should_close_conn = True
        self.db_ctx.transactions += 1
        logger.debug('Begin transaction...' if self.db_ctx.transactions == 1 else 'Join current transaction...')
        return self

    def __exit__(self, exctype, excvalue, traceback):
        self.db_ctx.transactions -= 1
        try:
            if self.db_ctx.transactions == 0:
                if exctype is None:
                    self.commit()
                else:
                    self.rollback()
        finally:
            if self.should_close_conn:
                self.db_ctx.release()

    def commit(self):
        try_commit(self.db_ctx)

    def rollback(self):
        logger.warning('Rollback transaction...')
        self.db_ctx.connection.rollback()
        logger.debug('Rollback ok.')


def get_connection():
    _DB_CTX.try_init()
    return _DB_CTX.connection


def close():
    global _DB_CTX
    global _POOLED

    if _POOLED:
        from .pooling import close_pool
        close_pool()
        _POOLED = False

    if _DB_CTX is not None:
        _DB_CTX.release()
        _DB_CTX = None


def execute(sql: str, *args) -> int:
    """
    Execute sql return effect rowcount

    :param sql: SQL
    :param args:
    :return: Effect rowcount

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'INSERT INTO person(name, age) VALUES(%s, %s)'
    >>> db.execute(sql, '张三', 20)
    1
    """

    cursor = None
    should_cleanup = False
    if _SHOW_SQL:
        do_sql_log(MODULE, 'execute', sql, *args)
    try:
        should_cleanup = _DB_CTX.try_init()
        cursor = _DB_CTX.cursor()
        cursor.execute(sql, args)
        result = cursor.rowcount
        if _DB_CTX.transactions == 0:
            try_commit(_DB_CTX)
        return result
    finally:
        if cursor:
            cursor.close()
        if should_cleanup:
            _DB_CTX.release()


def save(select_key: str, sql: str, *args) -> Any:
    """
    Execute sql return primary key

    :param select_key:
    :param sql: SQL
    :param args:
    :return: Primary key

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'INSERT INTO person(name, age) VALUES(%s, %s)'
    >>> db.save('SELECT LAST_INSERT_ID()', sql, '张三', 20)
    3
    """

    cursor = None
    should_cleanup = False
    if _SHOW_SQL:
        do_save_log(MODULE, 'save', select_key, sql, *args)
    try:
        should_cleanup = _DB_CTX.try_init()
        cursor = _DB_CTX.cursor()
        cursor.execute(sql, args)
        cursor.execute(select_key)
        result = cursor.fetchone()[0]
        if _DB_CTX.transactions == 0:
            try_commit(_DB_CTX)
        return result
    finally:
        if cursor:
            cursor.close()
        if  should_cleanup:
            _DB_CTX.release()


def get(sql: str, *args) -> Any:
    """
    Execute select SQL and expected one int and only one int result, SQL contain 'limit'.
    MultiColumnsError: Expect only one column.

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT count(1) FROM person WHERE name=%s and age=%s LIMIT 1'
    >>> db.get(sql, '张三', 20)
    1
    """

    result = select_first(sql, *args)
    if result:
        if len(result) == 1:
            return result[0]
        msg = f"Exec func 'sqlexecutorx.get' expect only one column but {len(result)}."
        logger.error('%s  \n\t sql: %s \n\t args: %s' % (msg, sql, args))
        raise MultiColumnsError(msg)
    return None


def select(sql: str, *args) -> List[Tuple[Any, ...]]:
    """
    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s'
    >>> db.select(sql, '张三', 20)
    [(3, '张三', 20)]
    """
    return do_select(sql, *args)[0]


def select_first(sql: str, *args) -> Tuple[Any, ...]:
    """
    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s LIMIT 1'
    >>> db.select_first(sql, '张三', 20)
    (3, '张三', 20)
    """
    return do_select_first(sql, *args)[0]


def select_one(sql: str, *args) -> Tuple[Any, ...]:
    """
    Execute select SQL and expected one row and only one row result, SQL contain 'limit'.
    MultiRowsError: Expect only one row.

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s LIMIT 1'
    >>> db.select_one(sql, '张三', 20)
    (3, '张三', 20)
    """
    return do_select_one(sql, *args)[0]


def query(sql: str, *args) -> List[Dict[str, Any]]:
    """
    Execute select SQL and return list results(dict).

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s'
    >>> db.query(sql, '张三', 20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    """
    results, description = do_select(sql, *args)
    if results and description:
        names = list(map(lambda x: x[0], description))
        return list(map(lambda x: Dict(names, x), results))
    return results


def query_first(sql: str, *args) -> Dict[str, Any]:
    """
    Execute select SQL and return unique result(dict), SQL contain 'limit'.

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s LIMIT 1'
    >>> db.query_first(sql, '张三', 20)
    {'id': 3, 'name': '张三', 'age': 20}
    """

    result, description = do_select_first(sql, *args)
    if result and description:
        names = list(map(lambda x: x[0], description))
        return Dict(names, result)
    return result

def query_one(sql: str, *args) -> Dict[str, Any]:
    """
    Execute select SQL and return unique result(dict), SQL contain 'limit'.

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s LIMIT 1'
    >>> db.query_one(sql, '张三', 20)
    {'id': 3, 'name': '张三', 'age': 20}
    """

    result, description = do_select_one(sql, *args)
    if result and description:
        names = list(map(lambda x: x[0], description))
        return Dict(names, result)
    return result


def ravel_list(sql: str, *args, position: int = 0) -> List:
    """
    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT name FROM person WHERE age=%s'
    >>> db.ravel_list(sql, '张三', 20)
    ['张三', '李四', '王五']
    """
    return [r[position] for r in select(sql, *args)]


def do_select(sql: str, *args) -> Tuple[List[Tuple[Any, ...]], Tuple[Tuple[str, Any, Any], ...]]:
    """
    Execute select SQL and return results and description

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s limit 1'
    >>> db.do_select(sql, '张三', 20)
    ([(3, '张三', 20)], (('id', None, None), ('name', None, None), ('age', None, None)))
    """

    cursor = None
    should_cleanup = False
    if _SHOW_SQL:
        do_sql_log(MODULE, 'do_select', sql, *args)

    try:
        should_cleanup = _DB_CTX.try_init()
        cursor = _DB_CTX.cursor()
        cursor.execute(sql, args)
        return cursor.fetchall(), cursor.description
    finally:
        if cursor:
            cursor.close()
        if should_cleanup:
            _DB_CTX.release()


def do_select_first(sql: str, *args) -> Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any, Any], ...]]:
    """
    Execute select SQL and return result and description

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s limit 1'
    >>> db.do_select_first(sql, '张三', 20)
    ((3, '张三', 20), (('id', None, None), ('name', None, None), ('age', None, None)))
    """

    if require_limit(sql):
        sql = limit_sql(sql, LIMIT_1)

    return _do_select_first(sql, *args)


def _do_select_first(sql: str, *args) -> Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any, Any], ...]]:
    cursor = None
    should_cleanup = False

    if _SHOW_SQL:
        do_sql_log(MODULE, '_do_select_first', sql, *args)

    try:
        should_cleanup = _DB_CTX.try_init()
        cursor = _DB_CTX.cursor()
        cursor.execute(sql, args)
        return cursor.fetchone(), cursor.description
    finally:
        if cursor:
            cursor.close()
        if should_cleanup:
            _DB_CTX.release()


def do_select_one(sql: str, *args) -> Tuple[Tuple[Any, ...], Tuple[Tuple[str, Any, Any], ...]]:
    """
    Execute select SQL and return result and description
    MultiRowsError: Expect only one row.

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s limit 1'
    >>> db.do_select_one(sql, '张三', 20)
    ((3, '张三', 20), (('id', None, None), ('name', None, None), ('age', None, None)))
    """

    if require_limit(sql):
        sql = limit_sql(sql, LIMIT_2)
        data, description = do_select(sql, *args)
        if len(data) == 1:
            return data[0], description
        elif len(data) == 0:
            return None, description

        msg = f"Exec func 'sqlexecutorx.do_select_one' expect only one row but {len(data)}."
        logger.error('%s  \n\t sql: %s \n\t args: %s' % (msg, sql, args))
        raise MultiRowsError(msg)
    else:
        return _do_select_first(sql, *args)


def batch_execute(sql: str, *args) -> int:
    """
    Batch execute sql return effected rowcount

    :param sql: SQL to execute
    :param args: All number must have same size.
    :return: Effect rowcount

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> args = [('张三', 20), ('李四', 28)]
    >>> sql = 'INSERT INTO person(name, age) VALUES(%s, %s)'
    >>> db.batch_execute(sql, args)
    2
    >>> db.batch_execute(sql, *args)
    2
    """

    cursor = None
    should_cleanup = False
    assert args, "*args must not be empty."
    assert is_tuple_or_list(args[0]), "args must not be Tuple or List."
    
    if len(args) == 1 and len(args[0]) > 0 and is_tuple_or_list(args[0][0]):
        args = args[0]
        
    if _SHOW_SQL:
        batch_sql_log(MODULE, 'batch_execute', sql, args)

    try:
        should_cleanup = _DB_CTX.try_init()
        cursor = _DB_CTX.cursor()
        cursor.executemany(sql, args)
        effect_rowcount = cursor.rowcount
        if _DB_CTX.transactions == 0:
            try_commit(_DB_CTX)
        return effect_rowcount
    finally:
        if cursor:
            cursor.close()
        if should_cleanup:
            _DB_CTX.release()
            
            
def page_select(count_sql: str, sql: str, *args) -> Tuple[int, Tuple[List, Tuple]]:
    """
    Execute select SQL and return total and list results(tuple).

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> count_sql = 'SELECT count(1) FROM person WHERE name=%s and age=%s'
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s limit %s, %s'
    >>> db.page_select(count_sql, sql, '张三', 20, 0, 10)
    (1, [(3, '张三', 20)])
    """
    return _page_select(count_sql, sql, *args)[:2]


def page_query(count_sql: str, sql: str, *args) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Execute select SQL and return total and list results(dict).

    Examples
    --------
    >>> import sqlexecutorx as db
    >>> count_sql = 'SELECT count(1) FROM person WHERE name=%s and age=%s'
    >>> sql = 'SELECT id, name, age FROM person WHERE name=%s and age=%s limit %s, %s'
    >>> db.page_query(count_sql, sql, '张三', 20, 0, 10)
    (1, [{'id': 3, 'name': '张三', 'age': 20}])
    """
    total, results, description = _page_select(count_sql, sql, *args)
    if results and description:
        names = list(map(lambda x: x[0], description))
        return total, list(map(lambda x: Dict(names, x), results))
    return total, results
      
            
def _page_select(count_sql: str, sql: str, *args):
    cursor = None
    should_cleanup = False
    if _SHOW_SQL:
        page_log(MODULE, '_page_select', count_sql, sql, *args)
        
    count_args = args[:-2] if len(args) > 2 else ()
    
    try:
        should_cleanup = _DB_CTX.try_init()
        cursor = _DB_CTX.cursor()
        cursor.execute(count_sql, count_args)
        total = cursor.fetchone()[0]
        cursor.execute(sql, args)
        return total, cursor.fetchall(), cursor.description
    finally:
        if cursor:
            cursor.close()
        if should_cleanup:
            _DB_CTX.release()
