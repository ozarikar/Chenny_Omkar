import re
from typing import Collection, Mapping
from sqlexecutorx import DBError
from functools import lru_cache
from sqlexecutorx.sql_support import require_limit, limit_sql, is_tuple_or_list
from sqlexecutorx.conf import lru_cache_size

from .dialect import Dialect
from .log_support import sql_log
from .constant import NAMED_REGEX, LIMIT_1

PATTERN = re.compile(NAMED_REGEX)


def limit_sql_args(sql: str, limit: int, *args):
    if require_limit(sql):
        return limit_sql(sql), (*args, limit)
    return sql, args


def insert_sql(table: str, cols: Collection[str]):
    tmp = []
    for col in cols:
        if ',' in col:
            tmp.extend([col.strip() for col in col.split(',')])
        else:
            tmp.append(col.strip())
    cols = tuple(tmp)
    return Dialect.create_insert_sql(table, cols)


def insert_sql_args(table: str, **kwargs):
    cols, args = zip(*kwargs.items())
    sql = Dialect.create_insert_sql(table, cols)
    return sql, args


def get_batch_args(*args):
    return args[0] if len(args) == 1 and is_tuple_or_list(args[0]) and len(args[0]) > 0 and is_tuple_or_list_dict(args[0][0]) else args


def is_tuple_or_list_dict(x):
    return is_tuple_or_list(x) or isinstance(x, Mapping)


def batch_insert_sql_args(table: str, *args):
    args = [zip(*arg.items()) for arg in args]  # [(cols, args)]
    cols, args = zip(*args)  # (cols), (args)
    sql = Dialect.create_insert_sql(table, cols[0])
    return sql, args


def batch_named_sql_args(sql: str, *args):
    args = [get_named_args(sql, **arg) for arg in args]
    sql = get_named_sql(sql)
    return sql, args


@lru_cache(maxsize=lru_cache_size)
def get_named_sql(sql: str):
    return re.sub(NAMED_REGEX, '?', sql)


def get_named_args(sql: str, **kwargs):
    return [kwargs[r[1:]] for r in re.findall(NAMED_REGEX, sql)]


def get_named_sql_args(sql: str, **kwargs):
    args = get_named_args(sql, **kwargs)
    return get_named_sql(sql), args


@lru_cache(maxsize=lru_cache_size)
def is_mapping(sql: str):
    return ':' in sql and re.search(PATTERN, sql) is not None


def is_placeholder(sql: str):
    return '?' in sql


def get_mapping_sql_args(sql: str, *args, **kwargs):
    if is_placeholder(sql):
        if args:
            return sql, args
        raise DBError("Placeholder sql expected '*args' but empty.")
    
    if is_mapping(sql):
        assert kwargs, "Named mapping SQL expected '**kwargs' empty."
        return get_named_sql_args(sql, **kwargs)

    return sql, args


def try_mapping(function, sql, *args, **kwargs):
    sql_log(function, sql, *args, **kwargs)
    return get_mapping_sql_args(sql, *args, **kwargs)
