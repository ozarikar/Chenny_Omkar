from typing import Any, List, Tuple
from . import sql_holder as holder
from .sql_support import get_batch_args
from .log_support import logger, sql_id_log, page_sql_id_log
from . import db


def save(sql_id: str, *args, **kwargs) -> Any:
    """
    Execute insert SQL, return primary key.
    :return: Primary key
    """
    sql_id_log('save', sql_id, *args, **kwargs)
    sql, args = _get_sql_args_from_id(f'execute', sql_id, *args, **kwargs)
    return db.do_save_sql(sql, *args)


def execute(sql_id: str, *args, **kwargs) -> int:
    """
    Execute SQL.
    sql: INSERT INTO person(name, age) VALUES(?, ?)  -->  args: ('张三', 20)
         INSERT INTO person(name, age) VALUES(:name,:age)  -->  kwargs: {'name': '张三', 'age': 20}
    """
    sql, args = _get_sql_args_from_id('execute', sql_id, *args, **kwargs)
    return db.do_execute(sql, *args)


def batch_execute(sql_id: str, *args) -> int:
    """
    Batch execute
    sql: INSERT INTO person(name, age) VALUES(?, ?)  -->  args: [('张三', 20), ('李四', 28)]
         INSERT INTO person(name, age) VALUES(:name,:age)  -->  args: [{'name': '张三', 'age': 20}, {'name': '李四', 'age': 28}]
    :return: Effect row count
    """
    logger.debug("Exec func f'{MODULE}dbx.%s' \n\t sql_id: '%s' \n\t args: %s" % ('batch_execute', sql_id, args))
    assert len(args) > 0, 'args must not be empty.'
    args = get_batch_args(*args)
    sql, _ = holder.do_get_sql(holder.get_sql_model(sql_id), True, None, *args)
    return db.batch_execute(sql, *args)


# ----------------------------------------------------------Query function------------------------------------------------------------------
def get(sql_id: str, *args, **kwargs) -> Any:
    """
    Execute select SQL and expected one int and only one int result. Automatically add 'limit ?' behind the sql statement if not.
    MultiColumnsError: Expect only one column.
    sql: SELECT count(1) FROM person WHERE name=? and age=? limit 1  -->  args: ('张三', 20)
         SELECT count(1) FROM person WHERE name=:name and age=:age limit 1  -->  kwargs: ('张三', 20) --> kwargs: {'name': '张三', 'age': 20}
    """
    sql, args = _get_sql_args_from_id('get', sql_id, *args, **kwargs)
    return db.do_get(sql, *args)


def query(sql_id: str, *args, **kwargs) -> List[dict]:
    """
    Execute select SQL and return list or empty list if no result.
    sql: SELECT * FROM person WHERE name=? and age=?  -->  args: ('张三', 20)
         SELECT * FROM person WHERE name=:name and age=:age  -->  kwargs: ('张三', 20) --> kwargs: {'name': '张三', 'age': 20}
    """
    sql, args = _get_sql_args_from_id('query', sql_id, *args, **kwargs)
    return db.do_query(sql, *args)


def query_one(sql_id: str, *args, **kwargs) -> dict:
    """
    Execute select SQL and expected one row result(dict). Automatically add 'limit ?' behind the sql statement if not.
    If no result found, return None.
    If multiple results found, the first one returned.
    sql: SELECT * FROM person WHERE name=? and age=? limit 1 -->  args: ('张三', 20)
         SELECT * FROM person WHERE name=:name and age=:age limit 1  -->  kwargs: ('张三', 20) --> kwargs: {'name': '张三', 'age': 20}
    """
    sql, args = _get_sql_args_from_id('query_one', sql_id, *args, **kwargs)
    return db.do_query_one(sql, *args)


def query_first(sql_id: str, *args, **kwargs) -> dict:
    """
    Execute select SQL and return first row result(dict).
    If no result found, return None.
    sql: SELECT * FROM person WHERE name=? -->  args: ('张三',)
         SELECT * FROM person WHERE name=:name  -->  kwargs: {'name': '张三'}
    """
    sql, args = _get_sql_args_from_id('query_first', sql_id, *args, **kwargs)
    return db.do_query_first(sql, *args)


def select(sql_id: str, *args, **kwargs) -> List[Tuple]:
    """
    Execute select SQL and return list(tuple) or empty list if no result.
    sql: SELECT * FROM person WHERE name=? and age=?  -->  args: ('张三', 20)
         SELECT * FROM person WHERE name=:name and age=:age   -->  kwargs: ('张三', 20) --> kwargs: {'name': '张三', 'age': 20}
    """
    sql, args = _get_sql_args_from_id('select', sql_id, *args, **kwargs)
    return db.do_select(sql, *args)


def select_one(sql_id: str, *args, **kwargs) -> Tuple:
    """
    Execute select SQL and expected one row result(tuple). Automatically add 'limit ?' behind the sql statement if not.
    If no result found, return None.
    If multiple results found, the first one returned.
    sql: SELECT * FROM person WHERE name=? and age=? limit 1  -->  args: ('张三', 20)
         SELECT * FROM person WHERE name=:name and age=:age limit 1  -->  kwargs: ('张三', 20) --> kwargs: {'name': '张三', 'age': 20}
    """
    sql, args = _get_sql_args_from_id('select_one', sql_id, *args, **kwargs)
    return db.do_select_one(sql, *args)


def select_first(sql_id: str, *args, **kwargs) -> Tuple:
    """
    Execute select SQL and return first row result(tuple).
    If no result found, return None.
    sql: SELECT * FROM person WHERE name=?  -->  args: ('张三',)
         SELECT * FROM person WHERE name=:name  -->  kwargs: {'name': '张三'}
    """
    sql, args = _get_sql_args_from_id('select_first', sql_id, *args, **kwargs)
    return db.do_select_first(sql, *args)


def query_page(sql_id: str, page_num=1, page_size=10, *args, **kwargs) -> List[dict]:
    """
    Execute select SQL and return list or empty list if no result. Automatically add 'limit ?,?' after sql statement if not.
    sql: SELECT * FROM person WHERE name=? and age=?  -->  args: ('张三', 20)
         SELECT * FROM person WHERE name=:name and age=:age  -->  kwargs: ('张三', 20) --> kwargs: {'name': '张三', 'age': 20}
    """
    page_sql_id_log('query_page', sql_id, page_num, page_size, *args, **kwargs)
    sql, args = holder.get_sql(sql_id, *args, **kwargs)
    return db.do_query_page(sql, page_num, page_size, *args)


def select_page(sql_id: str, page_num=1, page_size=10, *args, **kwargs) -> List[Tuple]:
    """
    Execute select SQL and return list or empty list if no result. Automatically add 'limit ?,?' after sql statement if not.
    sql: SELECT * FROM person WHERE name=? and age=?  -->  args: ('张三', 20)
         SELECT * FROM person WHERE name=:name and age=:age  -->  kwargs: ('张三', 20) --> kwargs: {'name': '张三', 'age': 20}
    """
    page_sql_id_log('select_page', sql_id, page_num, page_size, *args, **kwargs)
    sql, args = holder.get_sql(sql_id, *args, **kwargs)
    return db.do_select_page(sql, page_num, page_size, *args)


def _get_sql_args_from_id(function, sql_id: str, *args, **kwargs):
    sql_id_log(function, sql_id, *args, **kwargs)
    return holder.get_sql(sql_id, *args, **kwargs)


from .sql_id_exec import sql, page
