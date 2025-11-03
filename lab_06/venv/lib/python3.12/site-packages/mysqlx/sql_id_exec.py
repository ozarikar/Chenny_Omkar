from typing import Any
from . import dbx
from sqlexecx.sql_exec import SqlExec
from sqlexecx.page_exec import PageExec


class SqlIdExec(SqlExec):

    def save(self, *args, **kwargs) -> Any:
        """
        Insert data into table, return primary key.

        :param args:
        :return: Primary key
        """
        return self.exec.save(self.sql, *args, **kwargs)


def sql(sql_id: str) -> SqlIdExec:
    """
    Get a SqlIdExec instance

    Examples
    --------
    >>> from mysqlx import dbx
    >>> dbx.sql('user.select_all')
    SqlIdExec()
    """
    assert sql_id, "Parameter 'sql_id' must not be none"
    return SqlIdExec(dbx, sql_id)


def page(page_num: int, page_size: int) -> PageExec:
    """
    Get a PageExec instance

    Examples
    --------
    >>> from mysqlx import dbx
    >>> dbx.page(1, 10)
    PageExec()
    """
    return PageExec(dbx, page_num, page_size)
