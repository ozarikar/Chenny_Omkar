from . import db
from sqlexecx.sql_exec import SqlExec
from sqlexecx.page_exec import PageExec


def sql(sql: str) -> SqlExec:
    """
    Get a SqlExec instance

    Examples
    --------
    >>> from mysqlx import db
    >>> db.sql('SELECT id, name, age FROM person')
    SqlExec()
    """
    assert sql, "Parameter 'sql' must not be none"
    return SqlExec(db, sql)


def page(page_num: int, page_size: int) -> PageExec:
    """
    Get a PageExec instance

    Examples
    --------
    >>> from mysqlx import db
    >>> db.page(1, 10)
    PageExec()
    """
    return PageExec(db, page_num, page_size)
