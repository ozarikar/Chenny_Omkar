# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from functools import lru_cache
from typing import Tuple, List, Union, Any
from sqlexecutorx import batch_execute as _batch_execute
from .loader import Loader
from . import exec, sql_support
from .dialect import Dialect, Engine
from .constant import LIMIT_1, SELECT_COUNT, CACHE_SIZE
from .table_support import get_table_select_sql, get_where_arg_limit, WhereBase
from .table_limit_exec import LimitExec, ColumnLimitExec, WhereLimitExec, ColumnWhereLimitExec
from .table_page_exec import TablePageExec, ColumnPageExec, WherePageExec, ColumnWherePageExec
from .table_order_by import OrderByExec, ColumnOrderByExec, WhereOrderByExec, ColumnWhereOrderByExec


class ColumnWhereExec:

    def __init__(self, where_exec, *columns):
        self._where_exec = where_exec
        self.columns = columns

    def get(self) -> Any:
        """
        Select data from table and expected one int and only one int result, SQL contain 'limit'.
        MultiColumnsError: Expect only one column.

        sqlexecx.table('person').columns('name').where(id=1).get()
        """
        return self._where_exec.get(self.columns[0])

    def select(self) -> List[Tuple]:
        """
        Select data from table and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).select()
        [(3, '张三', 20)]
        """
        return self._where_exec.select(*self.columns)

    def select_one(self) -> Tuple:
        """
        Select data from table and return unique result(tuple), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).select_one()
        (3, '张三', 20)
        """
        return self._where_exec.select_one(*self.columns)

    def select_first(self) -> Tuple:
        """
        Select data from table and return first result(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三').select_first()
        (3, '张三', 20)
        """
        return self._where_exec.select_first(*self.columns)

    def query(self) -> List[dict]:
        """
        Select data from table and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).query()
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        return self._where_exec.query(*self.columns)

    def query_one(self) -> dict:
        """
        Select from table and return unique result(dict), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).query_one()
        {'id': 3, 'name': '张三', 'age': 20}
        """
        return self._where_exec.query_one(*self.columns)

    def query_first(self) -> dict:
        """
        Select from table and return first result(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三').query_first()
        {'id': 3, 'name': '张三', 'age': 20}
        """
        return self._where_exec.query_first(*self.columns)

    def ravel_list(self) -> List:
        """
        Select data from table and return list.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('name').where(age=20).ravel_list()
        ['张三', '李四', '王五']
        """
        return self._where_exec.ravel_list(*self.columns)

    def to_df(self):
        """
        Select from table and return pandas DataFrame instance.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name__eq='李四').to_df()
        """
        return self._where_exec.load(*self.columns).to_df()
    def to_pl(self):
        """
        Select from table and return polars DataFrame instance.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name__eq='李四').to_pl()
        """
        return self._where_exec.load(*self.columns).to_pl()

    def to_csv(self, file_name: str, delimiter=',', header=True, encoding='utf-8'):
        """
        Select from table and sava as a csv file.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db..table('person').columns('id', 'name', 'age').where(name__eq='李四').to_csv('test.csv')
        """
        self._where_exec.load(*self.columns).to_csv(file_name, delimiter, header, encoding)

    def to_json(self, file_name: str, encoding='utf-8'):
        """
        Select from table and sava as a json file.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db..table('person').columns('id', 'name', 'age').where(name__eq='李四').to_json('test.json')
        """
        self._where_exec.load(*self.columns).to_json(file_name, encoding)

    def page(self, page_num=1, page_size=10, return_total=False) -> ColumnWherePageExec:
        """
        Get a ColumnWherePageExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).page(1, 10)
        ColumnWherePageExec()
        """
        return ColumnWherePageExec(self._where_exec.page(page_num, page_size, return_total), *self.columns)

    def limit(self, limit: Union[int, Tuple[int], List[int]] = 10) -> ColumnWhereLimitExec:
        """
        Get a ColumnWhereLimitExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).limit(10)
        ColumnWhereLimitExec()
        """
        return ColumnWhereLimitExec(self._where_exec.limit(limit), *self.columns)
    
    def order_by(self, order_by: str) -> ColumnWhereOrderByExec:
        """
        Get a ColumnWhereOrderByExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20).order_by('id DESC, name ASC')
        ColumnWhereOrderByExec()
        """
        return ColumnWhereOrderByExec(self._where_exec.order_by(order_by), *self.columns)


class WhereExec(WhereBase):

    def __init__(self, _exec, table_name: str, order_by: str, **kwargs):
        super().__init__(_exec, table_name, order_by, **kwargs)

    def get(self, column: str) -> Any:
        """
        Select data from table and expected one int and only one int result, SQL contain 'limit'.

        MultiColumnsError: Expect only one column.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(id=3).get('name')
        张三
        """
        sql, args = self.get_select_one_sql_args(column)
        return self.exec.do_get(sql, *args, LIMIT_1)

    def count(self) -> int:
        """
        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三').count()
        1
        """
        return self.get(SELECT_COUNT)

    def exists(self) -> bool:
        """
        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三').exists()
        True
        """
        return self.get(1) == 1

    def select_one(self, *columns) -> Tuple:
        """
        Select data from table and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三', age=20).select_one('id', 'name', 'age')
        (3, '张三', 20)
        """
        sql, args = self.get_select_one_sql_args(*columns)
        return self.exec.do_select_one(sql, *args, LIMIT_1)

    def select_first(self, *columns) -> Tuple:
        """
        Select data from table and return first result(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三').select_first('id', 'name', 'age')
        (3, '张三', 20)
        """
        sql, args = self.get_select_sql_args(*columns)
        return self.exec.select_first(sql, *args)

    def query_one(self, *columns) -> dict:
        """
        Select from table and return unique result(dict), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三', age=20).query_one('id', 'name', 'age')
        {'id': 3, 'name': '张三', 'age': 20}
        """
        sql, args = self.get_select_one_sql_args(*columns)
        return self.exec.do_query_one(sql, *args, LIMIT_1)

    def query_first(self, *columns) -> dict:
        """
        Select from table and return first result(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三').query_first('id', 'name', 'age')
        {'id': 3, 'name': '张三', 'age': 20}
        """
        sql, args = self.get_select_sql_args(*columns)
        return self.exec.query_first(sql, *args)

    def delete(self) -> int:
        """
        Delete and return effect rowcount.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三').delete()
        1
        """
        where, args, _ = get_where_arg_limit(**self.where_condition)
        sql = 'DELETE FROM %s %s' % (Dialect.get_dialect_str(self.table), where)
        if Dialect.curr_engine() == Engine.MYSQL:
            sql = '{} LIMIT ?'.format(sql)
            args = [*args, LIMIT_1]
        return self.exec.do_execute(sql, *args)

    def update(self, **kwargs) -> int:
        """
        Update and return effect rowcount.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三').update(name='李四', age=45)
        1
        """
        where, args, _ = get_where_arg_limit(**self.where_condition)
        update_cols, update_args = zip(*kwargs.items())
        args = [*update_args, *args]
        update_cols = ', '.join(['{} = ?'.format(Dialect.get_dialect_str(col)) for col in update_cols])
        sql = 'UPDATE {} SET {} {}'.format(Dialect.get_dialect_str(self.table), update_cols, where)
        if Dialect.curr_engine() == Engine.MYSQL:
            sql = '{} LIMIT ?'.format(sql)
            args = [*args, LIMIT_1]
        return self.exec.do_execute(sql, *args)

    def columns(self, *columns) -> ColumnWhereExec:
        """
        Get a ColumnWhereExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三', age=20).columns('id', 'name', 'age')
        ColumnWhereExec()
        """
        return ColumnWhereExec(self, *columns)

    def page(self, page_num=1, page_size=10, return_total=False) -> WherePageExec:
        """
        Get a WherePageExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三', age=20).page(1, 10)
        WherePageExec()
        """
        return WherePageExec(self, page_num, page_size, return_total)

    def limit(self, limit: Union[int, Tuple[int], List[int]] = 10) -> WhereLimitExec:
        """
        Get a WhereLimitExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三', age=20).limit(10)
        WhereLimitExec()
        """
        return WhereLimitExec(self.exec, self.table, None, limit, **self.where_condition)
    
    def order_by(self, order_by: str) -> WhereOrderByExec:
        """
        Get a WhereOrderByExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').order_by('id DESC, name ASC')
        WhereOrderByExec()
        """
        return WhereOrderByExec(self.exec, self.table, order_by, **self.where_condition)
    
  
class ColumnExec:

    def __init__(self, table_exec, *columns):
        self.table_exec = table_exec
        self.columns = columns

    def insert(self, *args) -> int:
        """
        Insert data into table, return effect rowcount.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('name', 'age').insert('张三', 20)
        1
        """
        assert args, 'args expected but empty.'
        sql = sql_support.insert_sql(self.table_exec.table.strip(), self.columns)
        return self.table_exec.exec.execute(sql, *args)

    def batch_insert(self, *args) -> int:
        """
        Batch insert data into table and return effect rowcount

        Examples
        --------
        >>> import sqlexecx as db
        >>> args = [('张三', 20), ('李四', 28)]
        >>> db.table('person').columns('name', 'age').batch_insert(args)
        2
        >>> db.table('person').columns('name', 'age').batch_insert(*args)
        2
        """
        sql = sql_support.insert_sql(self.table_exec.table.strip(), self.columns)
        return _batch_execute(sql, *args)

    def get(self) -> Any:
        """
        Select data from table and expected one int and only one int result, SQL contain 'limit'.

        MultiColumnsError: Expect only one column.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('count(1)').get()
        3
        """
        return self.table_exec.get(*self.columns)

    def select(self) -> List[Tuple]:
        """
        Select data from table and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').select()
        [(3, '张三', 20)]
        """
        return self.table_exec.select(*self.columns)

    def select_one(self) -> Tuple:
        """
        Select data from table and return unique result(tuple), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').select_one()
        (3, '张三', 20)
        """
        return self.table_exec.select_one(*self.columns)

    def select_first(self) -> Tuple:
        """
        Select data from table and return first result(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').select_first()
        (3, '张三', 20)
        """
        return self.table_exec.select_first(*self.columns)

    def query(self) -> List[dict]:
        """
        Select data from table and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').query()
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        return self.table_exec.query(*self.columns)

    def query_one(self) -> dict:
        """
        Select from table and return unique result(dict), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').query_one()
        {'id': 3, 'name': '张三', 'age': 20}
        """
        return self.table_exec.query_one(*self.columns)

    def query_first(self) -> dict:
        """
        Select from table and return first result(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').query_first()
        {'id': 3, 'name': '张三', 'age': 20}
        """
        return self.table_exec.query_first(*self.columns)

    def ravel_list(self) -> List:
        """
        Select data from table and return list.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('name').ravel_list()
        ['张三', '李四', '王五']
        """
        return self.table_exec.ravel_list(*self.columns)

    def to_df(self):
        """
        Select from table and return pandas DataFrame instance.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').to_df()
        """
        return self.table_exec.load(*self.columns).to_df()
    
    def to_pl(self):
        """
        Select from table and return polars DataFrame instance.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').to_pl()
        """
        return self.table_exec.load(*self.columns).to_pl()

    def to_csv(self, file_name: str, delimiter=',', header=True, encoding='utf-8'):
        """
        Select from table and sava as a csv file.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db..table('person').columns('id', 'name', 'age').to_csv('test.csv')
        """
        self.table_exec.load(*self.columns).to_csv(file_name, delimiter, header, encoding)

    def to_json(self, file_name: str, encoding='utf-8'):
        """
        Select from table and sava as a json file.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db..table('person').columns('id', 'name', 'age').to_json('test.json')
        """
        self.table_exec.load(*self.columns).to_json(file_name, encoding)

    def where(self, **kwargs) -> ColumnWhereExec:
        """
        Get a ColumnWhereExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').where(name='张三', age=20)
        ColumnWhereExec()
        """
        return ColumnWhereExec(self.table_exec.where(**kwargs), *self.columns)

    def page(self, page_num=1, page_size=10, return_total=False) -> ColumnPageExec:
        """
        Get a ColumnPageExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').page(1, 10)
        ColumnPageExec()
        """
        return ColumnPageExec(self.table_exec.page(page_num, page_size, return_total), *self.columns)

    def limit(self, limit: Union[int, Tuple[int], List[int]] = 10) -> ColumnLimitExec:
        """
        Get a ColumnLimitExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').limit(10)
        ColumnLimitExec()
        """
        return ColumnLimitExec(self.table_exec.limit(limit), *self.columns)
    
    def order_by(self, order_by: str) -> ColumnOrderByExec:
        """
        Get a ColumnOrderByExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age').order_by('id DESC, name ASC')
        ColumnOrderByExec()
        """
        return ColumnOrderByExec(self.table_exec.order_by(order_by), *self.columns)


class Table:

    def __init__(self, _exec, table_name):
        self.exec = _exec
        self.table = table_name

    def insert(self, **kwargs) -> int:
        """
        Insert data into table, return effect rowcount.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').insert(name='张三', age=20)
        1
        """
        return self.exec.insert(self.table, **kwargs)

    def save(self, **kwargs) -> Any:
        """
        Insert data into table, return primary key.

        :return: Primary key

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').save(name='张三', age=20)
        3
        """
        return self.exec.save(self.table, **kwargs)

    def save_select_key(self, select_key: str, **kwargs) -> Any:
        """
        Insert data into table, return primary key.

        :param select_key: sql for select primary key
        :return: Primary key

        Examples
        --------
        >>> import sqlexecx as db
        >>> select_key = 'SELECT LAST_INSERT_ID()'
        >>> db.table('person').save_select_key(select_key, name='张三', age=20)
        3
        """
        return self.exec.save_select_key(select_key, self.table, **kwargs)

    def batch_insert(self, *args) -> int:
        """
        Batch insert data into table and return effect rowcount

        Examples
        --------
        >>> import sqlexecx as db
        >>> args = [{'name': '张三', 'age': 20}, {'name': '李四', 'age': 28}]
        >>> db.table('person').batch_insert(*args)
        2
        """
        return self.exec.batch_insert(self.table, *args)

    def get(self, column: str) -> Any:
        """
        Select data from table and expected one int and only one int result, SQL contain 'limit'.

        MultiColumnsError: Expect only one column.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').get('count(1)')
        3
        """
        sql = get_table_select_sql(self.table, None, None, LIMIT_1, column)
        return self.exec.do_get(sql, LIMIT_1)

    def count(self) -> int:
        """
        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').count()
        3
        """
        return self.get(SELECT_COUNT)

    def select(self, *columns) -> List[Tuple]:
        """
        Select data from table and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').select('id', 'name', 'age')
        [(3, '张三', 20)]
        """
        sql = get_table_select_sql(self.table, None, None, 0, *columns)
        return self.exec.do_select(sql)

    def select_one(self, *columns) -> Tuple:
        """
        Select data from table and return unique result(tuple), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').do_select_one('id', 'name', 'age')
        (3, '张三', 20)
        """
        sql = get_table_select_sql(self.table, None, None, LIMIT_1, *columns)
        return self.exec.do_select_one(sql, LIMIT_1)

    def select_first(self, *columns) -> Tuple:
        """
        Select data from table and return first result(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').select_first('id', 'name', 'age')
        (3, '张三', 20)
        """
        sql = get_table_select_sql(self.table, None, None, 0, *columns)
        return self.exec.select_first(sql)

    def query(self, *columns) -> List[dict]:
        """
        Select data from table and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').query('id', 'name', 'age')
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        sql = get_table_select_sql(self.table, None, None, 0, *columns)
        return self.exec.do_query(sql)

    def query_one(self, *columns) -> dict:
        """
        Select data from table and return unique result(dict), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').query_one('id', 'name', 'age')
        {'id': 3, 'name': '张三', 'age': 20}
        """
        sql = get_table_select_sql(self.table, None, None, LIMIT_1, *columns)
        return self.exec.do_query_one(sql, LIMIT_1)

    def query_first(self, *columns) -> dict:
        """
        Select data from table and return first result(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').query_first('id', 'name', 'age')
        {'id': 3, 'name': '张三', 'age': 20}
        """
        sql = get_table_select_sql(self.table, None, None, 0, *columns)
        return self.exec.query_first(sql)

    def ravel_list(self, column: str) -> List:
        """
        Select data from table and return list.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').ravel_list('name')
        ['张三', '李四', '王五']
        """
        sql = get_table_select_sql(self.table, None, None, 0, column)
        return self.exec.do_ravel_list(sql)

    def load(self, *columns) -> Loader:
        """
        Select from table and return a Loader instance

        :return: Loader

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').load('id', 'name', 'age')
        Lodder()
        """
        sql = get_table_select_sql(self.table, None, None, 0, *columns)
        return self.exec.do_load(sql)

    def insert_from_df(self, df, columns: Tuple[str] = None):
        """
        Insert data into table from pandas DataFrame and return effected rowcount.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').insert_from_df(df)
        20
        """
        return self.exec.insert_from_df(df, self.table, columns)
    def insert_from_pl(self, df, columns: Tuple[str] = None):
        """
        从polars DataFrame插入数据到表中并返回影响的行数。

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').insert_from_pl(df)
        20
        """
        return self.exec.insert_from_pl(df, self.table, columns)

    def insert_from_csv(self, file_name: str, delimiter=',', header=True, columns: Tuple[str] = None, encoding='utf-8'):
        """
        Insert data into table from a csv file and return effected rowcount.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').insert_from_csv('test.csv')
        20
        """
        return self.exec.insert_from_csv(file_name, self.table, delimiter, header, columns, encoding=encoding)

    def insert_from_json(self, file_name: str, encoding='utf-8'):
        """
        Insert data into table from a json file and return effected rowcount.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').insert_from_json('test.json')
        20
        """
        return self.exec.insert_from_json(file_name, self.table, encoding=encoding)

    def truncate(self) -> int:
        """
        Truncate table and return effected rowcount

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').truncate()
        1
        """
        return self.exec.truncate(self.table)

    def drop(self) -> int:
        """
        Drop table and return effected rowcount

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').drop()
        1
        """
        return self.exec.drop(self.table)

    def where(self, **kwargs) -> WhereExec:
        """
        Get a WhereExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').where(name='张三', age=20)
        WhereExec()
        """
        return WhereExec(self.exec, self.table, None, **kwargs)

    def columns(self, *columns) -> ColumnExec:
        """
        Get a ColumnExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').columns('id', 'name', 'age')
        ColumnExec()
        """
        return ColumnExec(self, *columns)

    def page(self, page_num=1, page_size=10, return_total=False) -> TablePageExec:
        """
        Get a TablePageExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').page(1, 10)
        TablePageExec()
        """
        return TablePageExec(self, page_num, page_size, return_total)

    def limit(self, limit: Union[int, Tuple[int], List[int]] = 10) -> LimitExec:
        """
        Get a LimitExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').limit(10)
        LimitExec()
        """
        return LimitExec(self.exec, self.table, None, limit)
    
    def order_by(self, order_by: str) -> OrderByExec:
        """
        Get a OrderByExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.table('person').order_by('id DESC, name ASC')
        OrderByExec()
        """
        return OrderByExec(self.exec, self.table, order_by)


@lru_cache(maxsize=CACHE_SIZE)
def table(table_name: str) -> Table:
    """
    Get a Table instance

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.table('person')
    Table()
    """
    table_name = table_name.strip()
    assert table_name, "Parameter 'table' must not be none"
    return Table(exec, table_name)
