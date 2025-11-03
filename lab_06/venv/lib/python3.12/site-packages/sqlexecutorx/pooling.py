from sqlexecutorx.support import DB_LOCK

_POOL = None
MAX_POOL_SIZE = 32


def pooled_connect(creator, pool_size, **kwargs):
    global _POOL
    assert 1 <= pool_size <= MAX_POOL_SIZE, 'pool_size should be higher or equal to 1 and lower or equal to {}'.format(MAX_POOL_SIZE)
    if _POOL is None:
        if 'mincached' not in kwargs:
            kwargs['mincached'] = pool_size
        if 'maxcached' not in kwargs:
            kwargs['maxcached'] = pool_size
        if 'maxconnections' not in kwargs:
            kwargs['maxconnections'] = MAX_POOL_SIZE

        with DB_LOCK:
            if _POOL is None:
                try:
                    from dbutils.pooled_db import PooledDB
                except ModuleNotFoundError:
                    raise ModuleNotFoundError("No module named 'dbutils', please install it use 'pip install DBUtils'")
                _POOL = PooledDB(creator, **kwargs)
    return _POOL.connection


def close_pool():
    global _POOL
    if _POOL:
        _POOL.close()
        _POOL = None

