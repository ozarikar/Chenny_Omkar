# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List, Tuple, Any
from functools import lru_cache
from sqlexecutorx.conf import lru_cache_size

from . import exec
from .loader import Loader
from .page_exec import PageExec


class SqlPageExec:

    def __init__(self, sql: str, page_exec: PageExec):
        self.sql = sql
        self.page_exec = page_exec

    def query(self, *args, **kwargs) -> List[dict]:
        """
        Execute select SQL and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').page(1, 10).query('张三', 20)
        [{'id': 3, 'name': '张三', 'age': 20}]
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').page(1, 10).query(name='张三', age=20)
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        return self.page_exec.query(self.sql, *args, **kwargs)

    def select(self, *args, **kwargs) -> List[Tuple]:
        """
        Execute select SQL and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').page(1, 10).select('张三', 20)
        [(3, '张三', 20)]
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').page(1, 10).select(name='张三', age=20)
        [(3, '张三', 20)]
        """
        return self.page_exec.select(self.sql, *args, **kwargs)

    def do_query(self, *args) -> List[dict]:
        """
        Execute select SQL and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').page(1, 10).do_query('张三', 20)
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        return self.page_exec.do_query(self.sql, *args)

    def do_select(self, *args) -> List[Tuple]:
        """
        Execute select SQL and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').page(1, 10).do_select('张三', 20)
        [(3, '张三', 20)]
        """
        return self.page_exec.do_select(self.sql, *args)


class ParamPageExec:

    def __init__(self, sql_page_exec: SqlPageExec, *args, **kwargs):
        self.sql_page_exec = sql_page_exec
        self.args = args
        self.kwargs = kwargs

    def query(self) -> List[dict]:
        """
        Execute select SQL and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').param('张三', 20).page(1, 10).query()
        [{'id': 3, 'name': '张三', 'age': 20}]
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').param(name='张三', age=20).page(1, 10).query()
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        return self.sql_page_exec.query(*self.args, **self.kwargs)

    def select(self) -> List[Tuple]:
        """
        Execute select SQL and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').param('张三', 20).page(1, 10).select()
        [(3, '张三', 20)]
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').param(name='张三', age=20).page(1, 10).select()
        [(3, '张三', 20)]
        """
        return self.sql_page_exec.select(*self.args, **self.kwargs)


class Param:

    def __init__(self, sql_exec, *args, **kwargs):
        self.sql_exec = sql_exec
        self.args = args
        self.kwargs = kwargs

    def execute(self) -> int:
        """
        Execute sql return effected rowcount

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('INSERT INTO person(name, age) VALUES(?, ?)').param('张三', 18).execute()
        1
        >>> db.sql('INSERT INTO person(name, age) VALUES(:name, :age)').param(name='张三', age=20).execute()
        1
        """
        return self.sql_exec.execute(*self.args, **self.kwargs)

    def save(self) -> Any:
        """
        Insert data into table, return primary key.

        :param args:
        :return: Primary key

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('INSERT INTO person(name, age) VALUES(?, ?)').param('张三', 18).save()
        3
        >>> db.sql('INSERT INTO person(name, age) VALUES(:name, :age)').param(name='张三', age=20).save()
        3
        """
        return self.sql_exec.save(*self.args, **self.kwargs)

    def save_select_key(self, select_key: str) -> Any:
        """
        Insert data into table, return primary key.

        :param select_key: sql for select primary key
        :param args:
        :return: Primary key

        Examples
        --------
        >>> import sqlexecx as db
        >>> select_key = 'SELECT LAST_INSERT_ID()'
        >>> db.sql('INSERT INTO person(name, age) VALUES(?, ?)').param('张三', 20).save_select_key(select_key)
        3
        >>> db.sql('INSERT INTO person(name, age) VALUES(:name, :age)').param(name='张三', age=20).save_select_key(select_key)
        3
        """
        return self.sql_exec.save_select_key(select_key, *self.args, **self.kwargs)

    def get(self) -> Any:
        """
        Execute select SQL and expected one int and only one int result, SQL contain 'limit'.

        MultiColumnsError: Expect only one column.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT count(1) FROM person WHERE name=? and age=? LIMIT 1').param('张三', 18).get()
        1
        >>> db.sql('SELECT count(1) FROM person WHERE name=:name and age=:age LIMIT 1').param(name='张三', age=20).get()
        1
        """
        return self.sql_exec.get(*self.args, **self.kwargs)

    def select(self) -> List[Tuple]:
        """
        Execute select SQL and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').param('张三', 18).select()
        [(3, '张三', 20)]
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').param(name='张三', age=20).select()
        [(3, '张三', 20)]
        """
        return self.sql_exec.select(*self.args, **self.kwargs)

    def select_one(self) -> Tuple:
        """
        Execute select SQL and return unique result(tuple), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1').param('张三', 18).select_one()
        (3, '张三', 20)
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age LIMIT 1').param(name='张三', age=20).select_one()
        (3, '张三', 20)
        """
        return self.sql_exec.select_one(*self.args, **self.kwargs)

    def select_first(self) -> Tuple:
        """
        Execute select SQL and return first result(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=?').param('张三').select_first()
        (3, '张三', 20)
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name').param(name='张三').select_first()
        (3, '张三', 20)
        """
        return self.sql_exec.select_first(*self.args, **self.kwargs)

    def query(self) -> List[dict]:
        """
        Execute select SQL and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').param('张三', 20).query()
        [{'id': 3, 'name': '张三', 'age': 20}]
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').param(name='张三', age=20).query()
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        return self.sql_exec.query(*self.args, **self.kwargs)

    def query_one(self) -> dict:
        """
        Execute select SQL and return unique result(dict), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').param('张三', 20).query_one()
        {'id': 3, 'name': '张三', 'age': 20}
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').param(name='张三', age=20).query_one()
        {'id': 3, 'name': '张三', 'age': 20}
        """
        return self.sql_exec.query_one(*self.args, **self.kwargs)

    def query_first(self) -> dict:
        """
        Execute select SQL and return first result(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=?').param('张三').query_first()
        {'id': 3, 'name': '张三', 'age': 20}
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name').param(name='张三').query_first()
        {'id': 3, 'name': '张三', 'age': 20}
        """
        return self.sql_exec.query_first(*self.args, **self.kwargs)

    def ravel_list(self, position: int = 0) -> List:
        """
        Execute select SQL and return list.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT name FROM person WHERE age=?').param(20).ravel_list()
        ['张三', '李四', '王五']
        >>> db.sql('SELECT name FROM person WHERE age=:age').param(age=20).ravel_list()
        ['张三', '李四', '王五']
        """
        return self.sql_exec.ravel_list(*self.args, position=position **self.kwargs)

    def to_df(self):
        """
        Execute select SQL and return pandas DataFrame instance.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT * FROM person WHERE name=? and age=?').param('张三', 18).to_df()
        pd.DataFrame()
        """
        return self.sql_exec.load(*self.args, **self.kwargs).to_df()
    def to_pl(self):
        """
        执行查询SQL并返回polars DataFrame实例。

        示例
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT * FROM person WHERE name=? and age=?').param('张三', 18).to_pl()
        pl.DataFrame()
        """
        return self.sql_exec.load(*self.args, **self.kwargs).to_pl()

    def to_csv(self, file_name: str, delimiter=',', header=True, encoding='utf-8'):
        """
        Execute select SQL and sava as a csv file.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT * FROM person WHERE name=? and age=?').param('张三', 18).to_csv('test.csv')
        """
        self.sql_exec.load(*self.args, **self.kwargs).to_csv(file_name, delimiter, header, encoding)

    def to_json(self, file_name: str, encoding='utf-8'):
        """
        Execute select SQL and sava as a json file.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').param('张三', 18).to_json('test.json')
        """
        self.sql_exec.load(*self.args, **self.kwargs).to_json(file_name, encoding)

    def page(self, page_num=1, page_size=10) -> ParamPageExec:
        """
        Execute select SQL and return ParamPageExec instance.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').param('张三', 18).page(1, 10)
        ParamPageExec()
        """
        return ParamPageExec(self.sql_exec.page(page_num, page_size), *self.args, **self.kwargs)


class SqlExec:

    def __init__(self, _exec, sql: str):
        self.exec = _exec
        self.sql = sql

    def execute(self, *args, **kwargs) -> int:
        """
        Execute sql return effected rowcount

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('INSERT INTO person(name, age) VALUES(?, ?)').execute('张三', 20)
        1
        >>> db.sql('INSERT INTO person(name, age) VALUES(:name, :age)').execute(name='张三', age=20)
        1
        """
        return self.exec.execute(self.sql, *args, **kwargs)

    def save(self, *args, **kwargs) -> Any:
        """
        Insert data into table, return primary key.

        :param args:
        :return: Primary key

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('INSERT INTO person(name, age) VALUES(?, ?)').save('张三', 20)
        3
        >>> db.sql('INSERT INTO person(name, age) VALUES(:name, :age)').save(name='张三', age=20)
        3
        """
        return self.exec.save_sql(self.sql, *args, **kwargs)

    def save_select_key(self, select_key: str, *args, **kwargs) -> Any:
        """
        Insert data into table, return primary key.

        :param select_key: sql for select primary key
        :param args:
        :return: Primary key

        Examples
        --------
        >>> import sqlexecx as db
        >>> select_key = 'SELECT LAST_INSERT_ID()'
        >>> db.sql('INSERT INTO person(name, age) VALUES(?, ?)').save_select_key(select_key, '张三', 20)
        3
        >>> db.sql('INSERT INTO person(name, age) VALUES(:name, :age)').save_select_key(select_key, name='张三', age=20)
        3
        """
        return self.exec.save_sql_select_key(select_key, self.sql, *args, **kwargs)

    def get(self, *args, **kwargs) -> Any:
        """
        Execute select SQL and expected one int and only one int result, SQL contain 'limit'.

        MultiColumnsError: Expect only one column.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT count(1) FROM person WHERE name=? and age=? LIMIT 1').get('张三', 20)
        1
        >>> db.sql('SELECT count(1) FROM person WHERE name=:name and age=:age LIMIT 1').get(name='张三', age=20)
        1
        """
        return self.exec.get(self.sql, *args, **kwargs)

    def select(self, *args, **kwargs) -> List[Tuple]:
        """
        Execute select SQL and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').select('张三', 20)
        [(3, '张三', 20)]
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').select(name='张三', age=20)
        [(3, '张三', 20)]
        """
        return self.exec.select(self.sql, *args, **kwargs)

    def select_one(self, *args, **kwargs) -> Tuple:
        """
        Execute select SQL and return unique result(tuple), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1').select_one('张三', 20)
        (3, '张三', 20)
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age LIMIT 1').select_one(name='张三', age=20)
        (3, '张三', 20)
        """
        return self.exec.select_one(self.sql, *args, **kwargs)

    def select_first(self, *args, **kwargs) -> Tuple:
        """
        Execute select SQL and return first result(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=?').select_first('张三')
        (3, '张三', 20)
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name').select_first(name='张三')
        (3, '张三', 20)
        """
        return self.exec.select_first(self.sql, *args, **kwargs)

    def query(self, *args, **kwargs) -> List[dict]:
        """
        Execute select SQL and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').query('张三', 20)
        [{'id': 3, 'name': '张三', 'age': 20}]
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').query(name='张三', age=20)
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        return self.exec.query(self.sql, *args, **kwargs)

    def query_one(self, *args, **kwargs) -> dict:
        """
        Execute select SQL and return unique result(dict), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').query_one('张三', 20)
        {'id': 3, 'name': '张三', 'age': 20}
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').query_one(name='张三', age=20)
        {'id': 3, 'name': '张三', 'age': 20}
        """
        return self.exec.query_one(self.sql, *args, **kwargs)

    def query_first(self, *args, **kwargs) -> dict:
        """
        Execute select SQL and return first result(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=?').query_first('张三')
        {'id': 3, 'name': '张三', 'age': 20}
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name').query_first(name='张三')
        {'id': 3, 'name': '张三', 'age': 20}
        """
        return self.exec.query_first(self.sql, *args, **kwargs)

    def ravel_list(self, *args, position: int = 0, **kwargs) -> List:
        """
        Execute select SQL and return list.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT name FROM person WHERE age=?').ravel_list(20)
        ['张三', '李四', '王五']
        >>> db.sql('SELECT name FROM person WHERE age=:age').ravel_list(age=20)
        ['张三', '李四', '王五']
        """
        return self.exec.ravel_list(self.sql, *args, position=position, **kwargs)

    def do_execute(self, *args) -> int:
        """
        Execute sql return effected rowcount

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('INSERT INTO person(name, age) VALUES(?, ?)').do_execute('张三', 20)
        1
        """
        return self.exec.do_execute(None, self.sql, *args)

    def do_save_sql(self, select_key: str, *args) -> Any:
        """
        Insert data into table, return primary key.

        :param select_key: sql for select primary key
        :param args:
        :return: Primary key

        Examples
        --------
        >>> import sqlexecx as db
        >>> select_key = 'SELECT LAST_INSERT_ID()'
        >>> db.sql('INSERT INTO person(name, age) VALUES(?, ?)').do_save_sql(select_key, '张三', 20)
        3
        """
        return self.exec.do_save_sql(select_key, self.sql, *args)

    def do_get(self, *args) -> Any:
        """
        Execute select SQL and expected one int and only one int result, SQL contain 'limit'.

        MultiColumnsError: Expect only one column.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT count(1) FROM person WHERE name=? and age=? LIMIT 1').do_get('张三', 20)
        1
        """
        return self.exec.do_get(self.sql, *args)

    def do_select(self, *args) -> List[Tuple]:
        """
        Execute select SQL and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1').do_select('张三', 20)
        (3, '张三', 20)
        """
        return self.exec.do_select(self.sql, *args)

    def do_select_one(self, *args) -> Tuple:
        """
        Execute select SQL and return unique result(tuple), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1').do_select_one('张三', 20)
        (3, '张三', 20)
        """
        return self.exec.do_select_one(self.sql, *args)

    def do_query(self, *args) -> List[dict]:
        """
        Execute select SQL and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').do_query('张三', 20)
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        return self.exec.do_query(self.sql, *args)

    def do_query_one(self, *args) -> dict:
        """
        execute select SQL and return unique result(dict), SQL contain 'limit'.

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').do_query_one('张三', 20)
        {'id': 3, 'name': '张三', 'age': 20}
        """
        return self.exec.do_query_one(self.sql, *args)

    def batch_execute(self, *args) -> int:
        """
        Batch execute sql return effected rowcount

        :param args: All number must have same size.
        :return: Effect rowcount

        Examples
        --------
        >>> import sqlexecx as db
        >>> args = [('张三', 20), ('李四', 28)]
        >>> db.sql('INSERT INTO person(name, age) VALUES(?, ?)').batch_execute(*args)
        2
        >>> args =  [{'name': '张三', 'age': 20}, {'name': '李四', 'age': 28}]
        >>> db.sql('INSERT INTO person(name, age) VALUES(:name, :age)').batch_execute(sql, *args)
        2
        """
        return self.exec.batch_execute(self.sql, *args)

    def load(self, *args, **kwargs) -> Loader:
        """
        Execute select SQL and return a Loader instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').load('张三', 20)
        Lodder()
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').load(name='张三', age=20)
        Lodder()
        """
        return self.exec.load(self.sql, *args, **kwargs)

    def do_load(self, *args) -> Loader:
        """
        Execute select SQL and return a Loader instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').load('张三', 20)
        Lodder()
        """
        return self.exec.do_load(self.sql, *args)

    def param(self, *args, **kwargs) -> Param:
        """
        Get a Param instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').param('张三', 20)
        Param()
        >>> db.sql('SELECT id, name, age FROM person WHERE name=:name and age=:age').param(name='张三', age=20)
        Param()
        """
        return Param(self, *args, **kwargs)

    def page(self, page_num=1, page_size=10) -> SqlPageExec:
        """
        Get a SqlPageExec instance

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.sql('SELECT id, name, age FROM person WHERE name=? and age=?').page(1, 10)
        SqlPageExec()
        """
        return SqlPageExec(self.sql, PageExec(self.exec, page_num=page_num, page_size=page_size))


@lru_cache(maxsize=lru_cache_size)
def sql(sql_text: str) -> SqlExec:
    """
    Get a SqlExec instance

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.sql('SELECT id, name, age FROM person')
    """

    sql_text = sql_text.strip()
    assert sql_text, "Parameter 'sql' must not be none"
    return SqlExec(exec, sql_text)
