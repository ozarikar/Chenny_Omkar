from logging import basicConfig, INFO, getLogger, Formatter, StreamHandler, DEBUG

logger = getLogger(__name__)
formatter = Formatter('[%(asctime)s %(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

handler = StreamHandler()
handler.setLevel(DEBUG)
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(INFO)


def db_ctx_log(action, connection):
    logger.debug(f"{action} connection <{hex(id(connection))}>...")


def do_sql_log(module: str, function: str, sql: str, *args):
    args = args if args else ''
    logger.info(f"Exec func '{module}.{function}' \n\tsql: {sql.strip()} \n\targs: {args}")


def batch_sql_log(module: str, function: str, sql: str, args):
    args = args if args else ''
    logger.info(f"Exec func '{module}.{function}' \n\tsql: {sql.strip()} \n\targs: {args}")


def do_save_log(module: str, function: str, select_key: str, sql: str, *args):
    args = args if args else ''
    logger.info(f"Exec func '{module}.{function}', select_key: '{select_key}' \n\tsql: {sql.strip()} \n\targs: {args}")
    
    
def page_log(module: str, function: str, count_sql: str, sql: str, *args):
    logger.info(f"Exec func '{module}.{function}', \n\tcount_sql: {count_sql} \n\tsql: {sql.strip()} \n\targs: {args}")
