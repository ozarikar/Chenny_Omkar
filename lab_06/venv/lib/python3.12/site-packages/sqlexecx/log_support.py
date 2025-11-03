from sqlexecutorx.log_support import logger, do_sql_log, do_save_log, batch_sql_log, db_ctx_log
from .constant import MODULE


def insert_log(function: str, table: str, **kwargs):
    logger.debug(f"Exec func '{MODULE}.{function}' \n\t Table: '{table}', kwargs: {kwargs}")


def save_log(function: str, select_key: str, table: str, **kwargs):
    logger.debug(f"Exec func '{MODULE}.{function}', 'select_key': {select_key} \n\t Table: '{table}', kwargs: {kwargs}")


def sql_log(function: str, sql: str, *args, **kwargs):
    logger.debug(f"Exec func '{function}' \n\tsql: {sql.strip()} \n\targs: {args} \n\tkwargs: {kwargs}")


def do_sql_log(function: str, sql: str, *args):
    logger.debug(f"Exec func '{function}' \n\t sql: {sql.strip()} \n\t args: {args}")

#
# def db_ctx_log(action, connection):
#     logger.debug("%s connection <%s>..." % (action, hex(id(connection))))

