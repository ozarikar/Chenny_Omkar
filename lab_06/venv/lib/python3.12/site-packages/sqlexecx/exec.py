from typing import Collection, Iterable, List, Tuple, Mapping, Any
from .loader import Loader
from .dialect import Dialect
from . import sql_support
from .constant import MODULE, LIMIT_1, LIMIT_2
from .log_support import logger, insert_log, save_log, batch_sql_log
from sqlexecutorx import execute as _execute, select as _select, select_one as _select_one, do_select as _do_select,\
    save as _save, batch_execute as _batch_execute, get as _get, query as _query, query_one as _query_one, DBError, \
    ravel_list as _ravel_list, select_first as _select_first, query_first as _query_first


def execute(sql: str, *args, **kwargs) -> int:
    """
    Execute sql return effect rowcount

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'INSERT INTO person(name, age) VALUES(?, ?)'
    >>> db.execute(sql, '张三', 20)
    1
    >>> sql = 'INSERT INTO person(name, age) VALUES(:name, :age)'
    >>> db.execute(sql, name='张三', age=20)
    1
    """

    sql, args = sql_support.try_mapping('sqlexecx.execute', sql, *args, **kwargs)
    return do_execute(sql, *args)


def insert(table_name: str, **kwargs) -> int:
    """
    Insert data into table, return effect rowcount.

    :param table_name: table name
    :param kwargs: {name='张三', age=20}
    return: Effect rowcount

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.insert('person', name='李四', age=18)
    1
    """

    insert_log('insert', table_name, **kwargs)
    sql, args = sql_support.insert_sql_args(table_name.strip(), **kwargs)
    return _execute(sql, *args)


def save(table_name: str, **kwargs) -> Any:
    """
    Insert data into table, return primary key.

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.save('person', name='李四', age=18)
    4
    """

    try:
        select_key = Dialect.get_select_key(table_name=table_name)
    except NotImplementedError:
        raise DBError(f"Expect 'select_key' but not. you may should use 'save_select_key' func with 'select_key'.")
    return save_select_key(select_key, table_name, **kwargs)


def save_sql(sql: str, *args, **kwargs) -> Any:
    """
    Insert data into table, return primary key.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'INSERT INTO person(name, age) VALUES(?, ?)'
    >>> db.save_sql(sql, '张三', 20)
    3
    >>> sql = 'INSERT INTO person(name, age) VALUES(:name, :age)'
    >>> db.save_sql(sql, name='张三', age=20)
    3
    """

    try:
        select_key = Dialect.get_select_key(sql=sql)
    except NotImplementedError:
        raise DBError(f"Expect 'select_key' but not. you may should use 'save_sql_select_key' func with 'select_key'.")
    return save_sql_select_key(select_key, sql, *args, **kwargs)


def save_select_key(select_key: str, table_name: str, **kwargs) -> Any:
    """
    Insert data into table, return primary key.

    :param select_key: sql for select primary key
    :param table_name: table name
    :param kwargs: {name='张三', age=20}
    :return: Primary key

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.save_select_key('SELECT LAST_INSERT_ID()', 'person', name='李四', age=18)
    4
    """

    save_log('save_select_key', select_key, table_name, **kwargs)
    sql, args = sql_support.insert_sql_args(table_name.strip(), **kwargs)
    return save_sql_select_key(select_key, sql, *args)


def save_sql_select_key(select_key: str, sql: str, *args, **kwargs) -> Any:
    """
    Insert data into table, return primary key.

    :param select_key: sql for select primary key
    :param sql: SQL
    :return: Primary key

    Examples
    --------
    >>> import sqlexecx as db
    >>> select_key = 'SELECT LAST_INSERT_ID()'
    >>> sql = 'INSERT INTO person(name, age) VALUES(?, ?)'
    >>> db.save_sql_select_key(select_key, sql, '张三', 20)
    3
    >>> sql = 'INSERT INTO person(name, age) VALUES(:name, :age)'
    >>> db.save_sql_select_key(select_key, sql, name='张三', age=20)
    3
    """

    logger.debug("Exec func 'sqlexecx.%s', 'select_key': %s \n\t sql: %s \n\t args: %s \n\t kwargs: %s" % ('save_sql', select_key, sql, args, kwargs))
    sql, args = sql_support.get_mapping_sql_args(sql, *args, **kwargs)
    return do_save_sql_select_key(select_key, sql, *args)


def get(sql: str, *args, **kwargs) -> Any:
    """
    Execute select SQL and expected one int and only one int result, SQL contain 'limit'.

    MultiColumnsError: Expect only one column.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT count(1) FROM person WHERE name=? and age=? LIMIT 1'
    >>> db.get(sql, '张三', 20)
    1
    >>> sql = 'SELECT count(1) FROM person WHERE name=:name and age=:age LIMIT 1'
    >>> db.get(sql, name='张三', age=20)
    1
    """

    sql, args = sql_support.try_mapping('sqlexecx.get', sql, *args, **kwargs)
    return do_get(sql, *args)


def select(sql: str, *args, **kwargs) -> List[Tuple]:
    """
    Execute select SQL and return list results(tuple).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.select(sql, '张三', 20)
    [(3, '张三', 20)]
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age '
    >>> db.get(sql, name='张三', age=20)
    [(3, '张三', 20)]
    """

    sql, args = sql_support.try_mapping('sqlexecx.select', sql, *args, **kwargs)
    return do_select(sql, *args)


def select_one(sql: str, *args, **kwargs) -> Tuple:
    """
    Execute select SQL and return unique result(tuple), SQL contain 'limit'.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1'
    >>> db.select_one(sql, '张三', 20)
    (3, '张三', 20)
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age LIMIT 1'
    >>> db.select_one(sql, name='张三', age=20)
    (3, '张三', 20)
    """

    sql, args = sql_support.try_mapping('sqlexecx.select_one', sql, *args, **kwargs)
    print('select_one: ========',sql, args)
    return do_select_one(sql, *args)


def query(sql: str, *args, **kwargs) -> List[dict]:
    """
    Execute select SQL and return list results(dict).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.query(sql, '张三', 20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age '
    >>> db.query(sql, name='张三', age=20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    """
    sql, args = sql_support.try_mapping('sqlexecx.query', sql, *args, **kwargs)
    return do_query(sql, *args)


def query_one(sql: str, *args, **kwargs) -> dict:
    """
    Execute select SQL and return unique result(dict), SQL contain 'limit'.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1'
    >>> db.query_one(sql, '张三', 20)
    {'id': 3, 'name': '张三', 'age': 20}
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age LIMIT 1'
    >>> db.query_one(sql, name='张三', age=20)
    {'id': 3, 'name': '张三', 'age': 20}
    """
    sql, args = sql_support.try_mapping('sqlexecx.query_one', sql, *args, **kwargs)
    return do_query_one(sql, *args)


def select_first(sql: str, *args, **kwargs) -> Tuple:
    """
    Execute select SQL and return first result(tuple).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.select_first(sql, '张三', 20)
    (3, '张三', 20)
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age'
    >>> db.select_first(sql, name='张三', age=20)
    (3, '张三', 20)
    """
    sql, args = sql_support.try_mapping('sqlexecx.select_first', sql, *args, **kwargs)
    return do_select_first(sql, *args)


def query_first(sql: str, *args, **kwargs) -> dict:
    """
    Execute select SQL and return first result(dict).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.query_first(sql, '张三', 20)
    {'id': 3, 'name': '张三', 'age': 20}
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age'
    >>> db.query_first(sql, name='张三', age=20)
    {'id': 3, 'name': '张三', 'age': 20}
    """
    sql, args = sql_support.try_mapping('sqlexecx.query_first', sql, *args, **kwargs)
    return do_query_first(sql, *args)


def ravel_list(sql: str, *args, position: int = 0, **kwargs) -> List:
    """
    Execute select SQL and return list.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT name, age FROM person WHERE age=?'
    >>> db.ravel_list(sql, 20)
    ['张三', '李四', '王五']
    >>> sql = 'SELECT id, name, age FROM person WHERE age=:age '
    >>> db.get(sql, age=20)
    ['张三', '李四', '王五']
    """

    sql, args = sql_support.try_mapping('sqlexecx.ravel_list', sql, *args, **kwargs)
    return do_ravel_list(sql, *args, position=position)


def do_execute(sql: str, *args) -> int:
    """
    Execute sql return effect rowcount

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'INSERT INTO person(name, age) VALUES(?, ?)'
    >>> db.do_execute(sql, '张三', 20)
    1
    """
    sql = Dialect.before_execute(sql)
    return _execute(sql, *args)


def do_save_sql(sql: str, *args) -> Any:
    """
    Insert data into table, return primary key.

    :param sql: SQL
    :param args:
    :return: Primary key

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'INSERT INTO person(name, age) VALUES(?, ?)'
    >>> db.do_save_sql(sql, '张三', 20)
    3
    """

    try:
        select_key = Dialect.get_select_key(sql=sql)
    except NotImplementedError:
        raise DBError(f"Expect 'select_key' but not. you may should use 'save_sql_select_key' func with 'select_key'.")
    return do_save_sql_select_key(select_key, sql, *args)


def do_save_sql_select_key(select_key: str, sql: str, *args) -> Any:
    """
    Insert data into table, return primary key.

    :param select_key: sql for select primary key
    :param sql: SQL
    :param args:
    :return: Primary key

    Examples
    --------
    >>> import sqlexecx as db
    >>> select_key = 'SELECT LAST_INSERT_ID()'
    >>> sql = 'INSERT INTO person(name, age) VALUES(?, ?)'
    >>> db.do_save_sql_select_key(select_key, sql, '张三', 20)
    3
    """

    sql = Dialect.before_execute(sql)
    return _save(select_key, sql, *args)


def do_get(sql: str, *args) -> Any:
    """
    Execute select SQL and expected one int and only one int result, SQL contain 'limit'.

    MultiColumnsError: Expect only one column.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT count(1) FROM person WHERE name=? and age=? LIMIT 1'
    >>> db.do_get(sql, '张三', 20)
    1
    """

    sql, args = sql_support.limit_sql_args(sql, LIMIT_1, *args)
    sql = Dialect.before_execute(sql)
    return _get(sql, *args)


def do_select(sql: str, *args) -> List[Tuple[Any, ...]]:
    """
    Execute select SQL and return list results(tuple).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.do_select(sql, '张三', 20)
    [(3, '张三', 20)]
    """

    sql = Dialect.before_execute(sql)
    return _select(sql, *args)


def do_select_one(sql: str, *args) -> Tuple[Any, ...]:
    """
    Execute select SQL and return unique result(tuple), SQL contain 'limit'.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1'
    >>> db.do_select_one(sql, '张三', 20)
    (3, '张三', 20)
    """

    print('do_select_one 1: ========',sql, args)
    sql, args = sql_support.limit_sql_args(sql, LIMIT_1, *args)
    sql = Dialect.before_execute(sql)
    print('do_select_one: ========',sql, args)
    return _select_one(sql, *args)


def do_query(sql: str, *args) -> List[dict[str, Any]]:
    """
    Execute select SQL and return list results(dict).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.do_query(sql, '张三', 20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    """

    sql = Dialect.before_execute(sql)
    return _query(sql, *args)


def do_query_one(sql: str, *args) -> dict[str, Any]:
    """
    Execute select SQL and return unique result(dict), SQL contain 'limit'.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1'
    >>> db.do_query_one(sql, '张三', 20)
    {'id': 3, 'name': '张三', 'age': 20}
    """

    sql, args = sql_support.limit_sql_args(sql, LIMIT_1, *args)
    sql = Dialect.before_execute(sql)
    return _query_one(sql, *args)


def do_select_first(sql: str, *args) -> Tuple[Any, ...]:
    """
    Execute select SQL and return first result(tuple).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.do_select_first(sql, '张三', 20)
    (3, '张三', 20)
    """

    sql, args = sql_support.limit_sql_args(sql, LIMIT_2, *args)
    sql = Dialect.before_execute(sql)
    return _select_first(sql, *args)


def do_query_first(sql: str, *args) -> dict:
    """
    Execute select SQL and return first result(dict).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.do_query_first(sql, '张三', 20)
    {'id': 3, 'name': '张三', 'age': 20}
    """

    sql, args = sql_support.limit_sql_args(sql, LIMIT_2, *args)
    sql = Dialect.before_execute(sql)
    return _query_first(sql, *args)


def do_ravel_list(sql: str, *args, position: int = 0) -> List:
    """
    Execute select SQL and return list results(tuple).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT name, age FROM person WHERE age=?'
    >>> db.do_ravel_list(sql, 20)
    ['张三', '李四', '王五']
    """

    sql = Dialect.before_execute(sql)
    return _ravel_list(sql, *args, position=position)


def select_page(sql: str, page_num=1, page_size=10, *args, **kwargs) -> List[Tuple]:
    """
    Execute select SQL and return list(tuple) or empty list if no result.

    Automatically add 'limit ?,?' after sql statement if not.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.select_page(sql, 1, 10, '张三', 20)
    [(3, '张三', 20)]
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age '
    >>> db.select_page(sql, 1, 10, name='张三', age=20)
    [(3, '张三', 20)]
    """

    sql, args = sql_support.try_mapping('select_page', sql, *args, **kwargs)
    return do_select_page(sql, page_num, page_size, *args)


def query_page(sql: str, page_num=1, page_size=10, *args, **kwargs) -> List[dict]:
    """
    Execute select SQL and return list or empty list if no result.

    Automatically add 'limit ?,?' after sql statement if not.

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.query_page(sql, 1, 10, '张三', 20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age '
    >>> db.query_page(sql, 1, 10, name='张三', age=20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    """
    sql, args = sql_support.try_mapping('query_page', sql, *args, **kwargs)
    return do_query_page(sql, page_num, page_size, *args)


def do_select_page(sql: str, page_num=1, page_size=10, *args) -> List[Tuple]:
    """
    Execute select SQL and return list results(dict).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.do_select_page(sql, 1, 10, '张三', 20)
    [(3, '张三', 20)]
    """

    sql, args = Dialect.get_page_sql_args(sql, page_num, page_size, *args)
    return do_select(sql, *args)


def do_query_page(sql: str, page_num=1, page_size=10, *args) -> List[dict]:
    """
    Execute select SQL and return list results(dict).

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.do_query_page(sql, 1, 10, '张三', 20)
    [{'id': 3, 'name': '张三', 'age': 20}]
    """

    sql, args = Dialect.get_page_sql_args(sql, page_num, page_size, *args)
    return do_query(sql, *args)


def batch_execute(sql: str, *args) -> int:
    """
    Batch execute

    :param sql: SQL to execute
    :param args: All number must have same size.
    :return: Effect row count

    Examples
    --------
    >>> import sqlexecx as db
    >>> args = [('张三', 20), ('李四', 28)]
    >>> sql = 'INSERT INTO person(name, age) VALUES(?, ?)'
    >>> db.batch_execute(sql, *args)
    2
    >>> args =  [{'name': '张三', 'age': 20}, {'name': '李四', 'age': 28}]
    >>> sql = 'INSERT INTO person(name, age) VALUES(:name, :age)'
    >>> db.batch_execute(sql, *args)
    2
    """

    batch_sql_log(MODULE, 'batch_execute', sql, args)
    assert args, "*args must not be empty."
    args = sql_support.get_batch_args(*args)
    if isinstance(args[0], Mapping):
        sql, args = sql_support.batch_named_sql_args(sql, *args)
    sql = Dialect.before_execute(sql)
    args = sql_support.get_batch_args(*args)
    return _batch_execute(sql, *args)


def batch_insert(table_name: str, *args) -> int:
    """
    Batch insert data into table and return effect rowcount

    :param table_name: table name
    :param args: All number must have same key. [{'name': '张三', 'age': 20}, {'name': '李四', 'age': 28}]
    :return: Effect row count

    Examples
    --------
    >>> import sqlexecx as db
    >>> args =  [{'name': '张三', 'age': 20}, {'name': '李四', 'age': 28}]
    >>> db.batch_execute('person', args)
    2
    >>> db.batch_execute('person', *args)
    2
    """
    
    logger.debug("Exec func 'sqlexecx.%s' \n\t Table: '%s', args: %s" % ('batch_insert', table_name, args))
    assert args, "*args must not be empty."
    args = sql_support.get_batch_args(*args)
    assert isinstance(args[0], Mapping), 'args must be a collection of Mapping'
    sql, args = sql_support.batch_insert_sql_args(table_name, *args)
    return _batch_execute(sql, *args)


def load(sql: str, *args, **kwargs) -> Loader:
    """
    Execute select SQL and return a Loader instance

    :param sql: SQL to be executed
    :return: Loader

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.load(sql, '张三', 20)
    Lodder()
    >>> sql = 'SELECT id, name, age FROM person WHERE name=:name and age=:age'
    >>> db.load(sql, name='张三', age=20)
    Lodder()
    """
    sql, args = sql_support.try_mapping('sqlexecx.csv', sql, *args, **kwargs)
    return do_load(sql, *args)


def do_load(sql: str, *args) -> Loader:
    """
    Execute select SQL and return a Loader instance

    :param sql: SQL to be executed
    :return: Loader

    Examples
    --------
    >>> import sqlexecx as db
    >>> sql = 'SELECT id, name, age FROM person WHERE name=? and age=?'
    >>> db.do_load(sql, '张三', 20)
    Lodder()
    """
    sql = Dialect.before_execute(sql)
    return Loader(*_do_select(sql, *args))


def insert_from_df(df, table_name: str, columns: Collection[str] = None) -> int:
    """
    Insert data into table from pandas DataFrame and return effected rowcount.

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.insert_from_df(df, 'person')
    """
    columns = columns if columns and len(columns) > 0 else df.columns.tolist()
    data = df.values.tolist()
    sql = sql_support.insert_sql(table_name.strip(), columns)
    return batch_execute(sql, data)


def insert_from_pl(df, table_name: str, columns: Collection[str] = None) -> int:
    """
    Insert data into table from polars DataFrame and return effected rowcount.

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.insert_from_df(df, 'person')
    """
    columns = columns if columns and len(columns) > 0 else df.columns
    data = df.to_numpy().tolist()
    sql = sql_support.insert_sql(table_name.strip(), columns)
    return batch_execute(sql, data)


def insert_from_csv(file_name: str, table_name: str, delimiter=',', header=True, columns: Collection[str] = None, encoding='utf-8') -> int:
    """
    Insert data into table from a csv file and return effected rowcount.

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.insert_from_csv('test.csv', 'person')
    20
    """

    import csv
    sql = None
    if columns and len(columns) > 0:
        sql = sql_support.insert_sql(table_name.strip(), columns)
    elif not header:
        raise ValueError("Expected one of 'header' and 'columns'.")

    with open(file_name, newline='', encoding=encoding) as f:
        lines = csv.reader(f, delimiter=delimiter)
        lines = [line for line in lines]

    if len(lines) == 0:
        return 0

    if header:
        if len(lines) == 1:
            return 0

        if sql is None:
            sql = sql_support.insert_sql(table_name.strip(), lines[0])
        lines = lines[1:]

    return batch_execute(sql, lines)


def insert_from_json(file_name: str, table_name: str, encoding='utf-8') -> int:
    """
    Insert data into table from a json file and return effected rowcount.

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.insert_from_json('test.json', 'person')
    20

    many rows json file example:
    [{"id": 1, "name": "张三", "age": 55}, ...]

    one row json file example:
    {"id": 1, "name": "张三", "age": 55}
    """

    import json

    with open(file_name, encoding=encoding) as f:
        data = json.load(f)

    if isinstance(data, dict):
        return insert(table_name, **data)
    elif isinstance(data, Iterable):
        return batch_insert(table_name, data)
    else:
        logger.info("Exec func 'sqlexecx.%s' \n\t Table: '%s' insert 0 rows." % ('insert_from_json', table_name))
        return 0


def truncate_table(table_name: str) -> int:
    """
    Truncate table

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.truncate_table('person')
    """
    return Dialect.truncate_table(table_name)


def drop_table(table_name: str) -> int:
    """
    Drop table

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.drop_table('person')
    """
    return _execute('DROP TABLE IF EXISTS %s' % Dialect.get_dialect_str(table_name))


def show_tables(schema: str = None) -> List[str]:
    """
    Show tables

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.show_tables()
    """
    return Dialect.show_tables(schema)
