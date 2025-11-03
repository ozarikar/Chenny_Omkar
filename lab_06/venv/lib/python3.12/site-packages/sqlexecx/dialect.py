# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
from functools import lru_cache
from typing import Sequence, Collection, Union, Optional
from sqlexecutorx.sql_support import require_limit
from sqlexecutorx import execute, get, query, select, DBError, Engine
from sqlexecutorx.conf import lru_cache_size

from .log_support import logger
from .constant import LIMIT_1, DEFAULT_KEY_FIELD, MYSQL_COLUMN_SQL, MYSQL_SELECT_KEY, POSTGRES_COLUMN_SQL, SQLITE_SELECT_KEY
from . import utils

NAMED_REGEX = r"like\s+'[\w|\d|%]*'"
PATTERN = re.compile(NAMED_REGEX, re.I)


def handle_like(sql: str):
    for r in re.finditer(PATTERN, sql):
        old = r.group()
        new = old.replace('%', '%%').replace('%%%%', '%%')
        sql = sql.replace(old, new, 1)
    return sql


class BaseDialect:

    def __init__(self, engine: Engine):
        self.engine = engine

    @staticmethod
    def create_insert_sql(table_name: str, cols: Collection[str], placeholder: str = '%s') -> str:
        columns, placeholders = zip(*[('{}'.format(col), placeholder) for col in cols])
        return f"INSERT INTO {table_name}({', '.join(columns)}) VALUES({','.join(placeholders)})"

    @staticmethod
    def before_execute(sql: str) -> str:
        if '%' in sql and 'like' in sql.lower():
            sql = handle_like(sql)
        return sql.replace('?', '%s')

    @staticmethod
    def get_page_sql_args(sql: str, page_num: int, page_size: int, *args):
        start = utils.get_page_start(page_num, page_size)
        if require_limit(sql):
            sql = BaseDialect.limit_offset_sql(sql)
        args = [*args, page_size, start]
        return sql, args

    @staticmethod
    def limit_offset_sql(sql: str):
        return f'{sql} LIMIT ? OFFSET ?'

    @staticmethod
    def get_table_columns(table_name: str) -> str:
        return '*'

    @staticmethod
    def truncate_table(table_name: str):
        return execute(f'TRUNCATE TABLE {Dialect.get_dialect_str(table_name)}')

    @staticmethod
    @lru_cache(maxsize=lru_cache_size)
    def get_dialect_str(src: Union[str, int, Collection[str]]) -> str:
        assert isinstance(src, str), 'source must be a string.'
        return src.strip() if isinstance(src, str) else ','.join([s.strip() for s in src])

    @staticmethod
    def get_select_key(*args, **kwargs):
        raise NotImplementedError("Not implement method 'get_select_key', you can use sqlormx snowflake for primary key.")

    @staticmethod
    def show_tables(schema: Optional[str]):
        return NotImplementedError


class MySQLDialect(BaseDialect):

    @staticmethod
    def create_insert_sql(table_name: str, cols: Sequence[str], placeholder: str = '%s') -> str:
        columns, placeholders = zip(*[('`{}`'.format(col), placeholder) for col in cols])
        return f"INSERT INTO `{table_name}`({','.join(columns)}) VALUES({','.join(placeholders)})"

    @staticmethod
    def get_page_sql_args(sql: str, page_num: int, page_size: int, *args):
        start = utils.get_page_start(page_num, page_size)
        if require_limit(sql):
            sql = MySQLDialect.limit_offset_sql(sql)
        args = [*args, start, page_size]
        return sql, args

    @staticmethod
    def limit_offset_sql(sql: str):
        return f'{sql} LIMIT ?, ?'

    @staticmethod
    @lru_cache(maxsize=lru_cache_size)
    def get_table_columns(table_name: str) -> str:
        return get(MYSQL_COLUMN_SQL, table_name, LIMIT_1)

    @staticmethod
    def get_select_key(*args, **kwargs) -> str:
        return MYSQL_SELECT_KEY

    @staticmethod
    @lru_cache(maxsize=lru_cache_size)
    def get_dialect_str(src: Union[str, int, Collection[str]]) -> str:
        assert src, 'src is required.'
        if isinstance(src, str):
            return _dialect_str(src)
        return ','.join([_dialect_str(arg) for arg in src])

    @staticmethod
    def show_tables(schema: Optional[str]):
        if schema:
            execute(f'use {schema}')
        return [table[0] for table in select('show tables')]


class PostgresDialect(BaseDialect):

    @staticmethod
    @lru_cache(maxsize=lru_cache_size)
    def get_table_columns(table_name: str) -> str:
        return get(POSTGRES_COLUMN_SQL, table_name, LIMIT_1)

    @staticmethod
    def get_select_key(key_seq: str = None, table_name: str = None, key: str =None, sql: str = None) -> str:
        if not key_seq:
            if table_name:
                key_seq = PostgresDialect.build_key_seq(table_name, key)
            else:
                if sql:
                    key_seq = PostgresDialect._get_key_seq_from_sql(sql)
                else:
                    raise DBError("Get PostgreSQL select key fail, all of 'key_seq', 'table', 'sql' are None")
        return f"SELECT currval('{key_seq}')"

    @staticmethod
    def build_key_seq(table_name: str, key: str = None) -> str:
        if not key:
            key = DEFAULT_KEY_FIELD
        return f'{table_name}_{key}_seq'

    @staticmethod
    @lru_cache(maxsize=lru_cache_size)
    def _get_key_seq_from_sql(sql: str) -> str:
        table_name = re.search('(?<=into )\w+', sql, re.I)
        key_seq = PostgresDialect.build_key_seq(table_name.group())
        logger.warning("'key_seq' is None, will use default '{}' from sql.".format(key_seq))
        return key_seq

    @staticmethod
    def show_tables(schema: Optional[str]):
        sql = '''
        SELECT tablename FROM pg_catalog.pg_tables  
         WHERE schemaname != 'pg_catalog'  
           AND schemaname != 'information_schema'
       '''
        if schema:
            execute(f'use {schema}')
        return [table[0] for table in select(sql)]


class OracleDialect(BaseDialect):

    @staticmethod
    def get_page_sql_args(sql: str, page_num: int, page_size: int, *args):
        start = utils.get_page_start(page_num, page_size)
        end = start + page_size
        sql = f'SELECT * FROM (SELECT tmp.*, rownum row_num FROM ({sql}) tmp WHERE rownum <= ?) WHERE row_num > ? '
        args = [*args, end, start]
        return sql, args

    @staticmethod
    @lru_cache(maxsize=lru_cache_size)
    def get_table_columns(table_name: str) -> str:
        sql = 'SELECT column_name FROM user_tab_columns WHERE table_name = %s'
        results = select(sql, table_name)
        return ','.join([result[0] for result in results])


class SQLiteDialect(MySQLDialect):
    
    @staticmethod
    def create_insert_sql(table_name: str, cols: Sequence[str], placeholder: str = '?') -> str:
        return MySQLDialect.create_insert_sql(table_name, cols, placeholder)

    @staticmethod
    @lru_cache(maxsize=lru_cache_size)
    def get_table_columns(table_name: str) -> str:
        results = query(f'PRAGMA table_info(`{table_name}`)')
        return ','.join([f"`{result['name']}`" for result in results])

    @staticmethod
    def get_select_key(*args, **kwargs) -> str:
        return SQLITE_SELECT_KEY

    @staticmethod
    def before_execute(sql: str) -> str:
        if '%' in sql and 'like' in sql.lower():
            sql = handle_like(sql)
        return sql

    @staticmethod
    def truncate_table(table_name: str) -> int:
        return execute(f'DELETE FROM `{table_name}`')

    @staticmethod
    def show_tables(schema: Optional[str]):
        return [table[0] for table in select("SELECT name FROM sqlite_master WHERE type='table'")]
    

_DIALECT = None


class Dialect:

    @classmethod
    def init(cls, engine: Engine):
        global _DIALECT
        if _DIALECT is None:
            if Engine.MYSQL == engine:
                _DIALECT = MySQLDialect(engine)
            elif Engine.POSTGRESQL == engine:
                _DIALECT = PostgresDialect(engine)
            elif Engine.ORACLE == engine:
                _DIALECT = OracleDialect(engine)
            elif Engine.SQLITE == engine:
                _DIALECT = SQLiteDialect(engine)
            else:
                _DIALECT = BaseDialect(engine)

    @staticmethod
    @lru_cache(maxsize=lru_cache_size)
    def create_insert_sql(table_name: str, cols: Collection[str]) -> str:
        return _DIALECT.create_insert_sql(table_name, cols)

    @staticmethod
    @lru_cache(maxsize=lru_cache_size)
    def before_execute(sql: str) -> str:
        return _DIALECT.before_execute(sql)

    @staticmethod
    def get_page_sql_args(sql: str, page_num: int, page_size: int, *args):
        return _DIALECT.get_page_sql_args(sql, page_num, page_size, *args)
    
    @staticmethod
    def limit_offset_sql(sql: str):
        return _DIALECT.limit_offset_sql(sql)

    @staticmethod
    def get_table_columns(table_name: str) -> str:
        return _DIALECT.get_table_columns(table_name)

    @staticmethod
    def truncate_table(table_name: str) -> int:
        return _DIALECT.truncate_table(table_name)

    @staticmethod
    def get_select_key(*args, **kwargs) -> str:
        return _DIALECT.get_select_key(*args, **kwargs)

    @staticmethod
    def get_dialect_str(src: Union[str, int, Collection[str]]) -> str:
        return _DIALECT.get_dialect_str(src)

    @staticmethod
    def curr_engine() -> Engine:
        return _DIALECT.engine

    @staticmethod
    def show_tables(schema: Optional[str]):
        return _DIALECT.show_tables(schema)


def _dialect_str(src: Union[str, int]):
    assert isinstance(src, str) or isinstance(src, int), 'source must be a string or int.'
    if isinstance(src, int):
        return str(src)
    elif '(' in src or ' as ' in src.lower():
        return src.strip()
    elif ',' in src:
        return ','.join([f"`{s.strip()}`"for s in src.split(',')])
    else:
        return f'`{src.strip()}`'
