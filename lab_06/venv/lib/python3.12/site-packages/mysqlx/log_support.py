# Don't remove. Import for not repetitive implementation
from sqlexecx.log_support import logger
from .constant import MODULE


def sql_id_log(function: str, sql_id: str, *args, **kwargs):
    logger.debug("Exec func '%s.dbx.%s', sql_id: %s, args: %s, kwargs: %s" % (MODULE, function, sql_id.strip(), args, kwargs))


def page_log(function: str, sql: str, page_num, page_size, *args, **kwargs):
    logger.debug("Exec func '%s.db.%s', page_num: %d, page_size: %d \n\tsql: %s \n\targs: %s \n\tkwargs: %s" % (
                 MODULE, function, page_num, page_size, sql.strip(), args, kwargs))


def page_sql_id_log(function: str, sql_id: str, page_num, page_size, *args, **kwargs):
    logger.debug("Exec func '%s.dbx.%s', page_num: %d, page_size: %d, sql_id: %s, args: %s, kwargs: %s" % (
    MODULE, function, page_num, page_size, sql_id, args, kwargs))
