# !/usr/bin/env python3
# -*- coding:utf-8 -*-

from typing import List, Tuple
from . import exec


class PageExec:

    def __init__(self, _exec, page_num, page_size):
        self.exec = _exec
        self.page_num = page_num
        self.page_size = page_size

    def query(self, sql: str, *args, **kwargs) -> List[dict]:
        """
        Execute select SQL and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.page(1, 10).query('SELECT id, name, age FROM person WHERE name=? and age=?', '张三', 20)
        [{'id': 3, 'name': '张三', 'age': 20}]
        >>> db.page(1, 10).query('SELECT id, name, age FROM person WHERE name=:name and age=:age', name='张三', age=20)
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        """
        Execute select SQL and return list or empty list if no result. Automatically add 'limit ?,?' after sql statement if not.
        sql: SELECT * FROM user WHERE name=? and age=?  -->  args: ('张三', 20)
             SELECT * FROM user WHERE name=:name and age=:age  -->  kwargs: ('张三', 20) --> kwargs: {'name': '张三', 'age': 20}
        """
        return self.exec.query_page(sql, self.page_num, self.page_size, *args, **kwargs)

    def select(self, sql: str, *args, **kwargs) -> List[Tuple]:
        """
        Execute select SQL and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.page(1, 10).select('SELECT id, name, age FROM person WHERE name=? and age=?', '张三', 20)
        [(3, '张三', 20)]
        >>> db.page(1, 10).select('SELECT id, name, age FROM person WHERE name=:name and age=:age', name='张三', age=20)
        [(3, '张三', 20)]
        """
        return self.exec.select_page(sql, self.page_num, self.page_size, *args, **kwargs)

    def do_query(self, sql: str, *args) -> List[dict]:
        """
        Execute select SQL and return list results(dict).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.page(1, 10).do_query('SELECT id, name, age FROM person WHERE name=? and age=?', '张三', 20)
        [{'id': 3, 'name': '张三', 'age': 20}]
        """
        return self.exec.do_query_page(sql, self.page_num, self.page_size, *args)

    def do_select(self, sql: str, *args) -> List[Tuple]:
        """
        Execute select SQL and return list results(tuple).

        Examples
        --------
        >>> import sqlexecx as db
        >>> db.page(1, 10).do_select('SELECT id, name, age FROM person WHERE name=? and age=? LIMIT 1', '张三', 20)
        (3, '张三', 20)
        """
        return self.exec.do_select_page(sql, self.page_num, self.page_size, *args)


def page(page_num=1, page_size=10) -> PageExec:
    """
    Get a PageExec instance

    Examples
    --------
    >>> import sqlexecx as db
    >>> db.page(1, 10)
    """
    return PageExec(exec, page_num, page_size)
