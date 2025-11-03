import threading
from .log_support import logger, db_ctx_log

DB_LOCK = threading.RLock()


def try_commit(db_ctx):
    if db_ctx.transactions == 0:
        logger.debug('Commit transaction...')
        try:
            db_ctx.connection.commit()
            logger.debug('Commit ok.')
        except Exception:
            logger.warning('Commit failed, try rollback...')
            db_ctx.connection.rollback()
            logger.warning('Rollback ok.')
            raise
        
        
class InitArgs:
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
        POOL_SIZE = 'pool_size'
    """
    HOST = 'host'
    PORT = 'port'
    USER = 'user'
    PASSWORD = 'password'
    DATABASE = 'database'
    DRIVER = 'driver'
    DEBUG = 'debug'
    SHOW_SQL = 'show_sql'
    POOL_SIZE = 'pool_size'


class DBCtx(threading.local):
    """
    Thread local object that holds connection info.
    """

    def __init__(self, connect, prepared=False):
        self.connect = connect
        self.connection = None
        self.transactions = 0
        self.prepared = prepared

    # def is_not_init(self):
    #     return self.connection is None

    def try_init(self):
        if self.connection is None:
            self.transactions = 0
            self.connection = self.connect()
            self.log('Use')
            return True
        return False

    def release(self):
        if self.connection:
            self.log('Release')
            self.connection.close()
            self.connection = None

    def cursor(self):
        """
        Return cursor
        """
        # logger.debug('Cursor prepared: %s' % self.prepared)
        return self.connection.cursor(prepared=True) if self.prepared else self.connection.cursor()

    def log(self, action: str):
        db_ctx_log(action, self.connection)


class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value
