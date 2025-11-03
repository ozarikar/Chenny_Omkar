from typing import List, Tuple, Any
from . import sql_support
# Don't remove. Import for not repetitive implementation
from sqlexecx import insert, save, batch_insert, batch_execute, do_execute, do_save_sql, do_get, do_query,\
    do_query_one, do_select, do_select_one, do_select_page, do_query_page, do_select_page, do_query_page, \
    load, do_load, insert_from_csv, insert_from_df, insert_from_json, truncate_table, drop_table, table, \
    do_select_first, do_query_first


def execute(sql: str, *args, **kwargs) -> int:
    """
    Execute sql return effect rowcount

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'INSERT INTO person(name, age) VALUES(?, ?)'
    >>> db.execute(sql, '张三', 20)
    1
    >>> sql = 'INSERT INTO person(name, age) VALUES(:name, :age)'
    >>> db.execute(sql, name='张三', age=20)
    1
    """
    sql, args = sql_support.try_dynamic_sql('MySQLX.db.execute', sql, *args, **kwargs)
    return do_execute(sql, *args)


def get(sql: str, *args, **kwargs) -> Any:
    """
    Execute select SQL and expected one int and only one int result, SQL contain 'limit'.

    MultiColumnsError: Expect only one column.

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'SELECT count(1) FROM person WHERE name=? and age=? LIMIT 1'
    >>> db.get(sql, '张三', 20)
    1
    >>> sql = 'SELECT count(1) FROM person WHERE name=:name and age=:age LIMIT 1'
    >>> db.get(sql, name='张三', age=20)
    1
    """
    sql, args = sql_support.try_dynamic_sql('MySQLX.db.get', sql, *args, **kwargs)
    return do_get(sql, *args)


def query(sql: str, *args, **kwargs) -> List[dict]:
    """
    Execute select SQL and return list results(dict).

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.query(sql, '张三', 20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age '
    >>> db.query(sql, name='张三', age=20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    """
    sql, args = sql_support.try_dynamic_sql('MySQLX.db.query', sql, *args, **kwargs)
    return do_query(sql, *args)


def query_one(sql: str, *args, **kwargs) -> dict:
    """
    Execute select SQL and return unique result(dict), SQL contain 'limit'.

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1'
    >>> db.query_one(sql, '张三', 20)
    {'id': 3, 'name': '张三', 'age': 20}
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age LIMIT 1'
    >>> db.query_one(sql, name='张三', age=20)
    {'id': 3, 'name': '张三', 'age': 20}
    """
    sql, args = sql_support.try_dynamic_sql('MySQLX.db.query_one', sql, *args, **kwargs)
    return do_query_one(sql, *args)


def query_first(sql: str, *args, **kwargs) -> dict:
    """
    Execute select SQL and return first result(dict).

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=?'
    >>> db.query_first(sql, '张三')
    {'id': 3, 'name': '张三', 'age': 20}
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name'
    >>> db.query_first(sql, name='张三')
    {'id': 3, 'name': '张三', 'age': 20}
    """
    sql, args = sql_support.try_dynamic_sql('MySQLX.db.query_first', sql, *args, **kwargs)
    return do_query_first(sql, *args)


def select(sql: str, *args, **kwargs) -> List[Tuple]:
    """
    Execute select SQL and return list results(tuple).

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.select(sql, '张三', 20)
    [(3, '张三', 20)]
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age '
    >>> db.get(sql, name='张三', age=20)
    [(3, '张三', 20)]
    """
    sql, args = sql_support.try_dynamic_sql('MySQLX.db.select', sql, *args, **kwargs)
    return do_select(sql, *args)


def select_one(sql: str, *args, **kwargs) -> Tuple:
    """
    Execute select SQL and return unique result(tuple), SQL contain 'limit'.

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1'
    >>> db.select_one(sql, '张三', 20)
    (3, '张三', 20)
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age LIMIT 1'
    >>> db.select_one(sql, name='张三', age=20)
    (3, '张三', 20)
    """
    sql, args = sql_support.try_dynamic_sql('MySQLX.db.select_one', sql, *args, **kwargs)
    return do_select_one(sql, *args)


def select_first(sql: str, *args, **kwargs) -> Tuple:
    """
    Execute select SQL and return first result(tuple).

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=?'
    >>> db.select_first(sql, '张三')
    (3, '张三', 20)
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name'
    >>> db.select_first(sql, name='张三')
    (3, '张三', 20)
    """
    sql, args = sql_support.try_dynamic_sql('MySQLX.db.select_first', sql, *args, **kwargs)
    return do_select_first(sql, *args)


def query_page(sql: str, page_num=1, page_size=10, *args, **kwargs) -> List[dict]:
    """
    Execute select SQL and return list or empty list if no result.

    Automatically add 'limit ?,?' after sql statement if not.

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.query_page(sql, 1, 10, '张三', 20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age '
    >>> db.query_page(sql, 1, 10, name='张三', age=20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    """
    sql, args = sql_support.try_page_mapping('query_page', sql, page_num, page_size, *args, **kwargs)
    return do_query_page(sql, page_num, page_size, *args)


def select_page(sql: str, page_num=1, page_size=10, *args, **kwargs) -> List[Tuple]:
    """
    Execute select SQL and return list(tuple) or empty list if no result.

    Automatically add 'limit ?,?' after sql statement if not.

    Examples
    --------
    >>> from mysqlx import db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.select_page(sql, 1, 10, '张三', 20)
    [(3, '张三', 20)]
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age '
    >>> db.select_page(sql, 1, 10, name='张三', age=20)
    [(3, '张三', 20)]
    """
    sql, args = sql_support.try_page_mapping('select_page', sql, page_num, page_size, *args, **kwargs)
    return do_select_page(sql, page_num, page_size, *args)


from .sql_page_exec import sql, page
