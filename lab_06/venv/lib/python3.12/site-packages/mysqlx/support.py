from enum import Enum
from sqlexecutorx import DBError, InitArgs as _InitArgs


class MapperError(DBError):
    pass


class NotFoundError(DBError):
    pass


class SqlAction(Enum):
    SQL = 'sql'
    CALL = 'call'
    INSERT = 'insert'
    UPDATE = 'update'
    DELETE = 'delete'
    SELECT = 'select'
    
    
class InitArgs(_InitArgs):
    """
    Args：
        HOST = 'host' \n
        PORT = 'port' \n
        USER = 'user' \n
        PASSWORD = 'password' \n
        DATABASE = 'database' \n
        DRIVER = 'driver' \n
        DEBUG = 'debug' \n
        SHOW_SQL = 'show_sql' \n
        POOL_SIZE = 'pool_size' \n
        MAPPER_PATH = 'mapper_path'
    """
    MAPPER_PATH = 'mapper_path'
