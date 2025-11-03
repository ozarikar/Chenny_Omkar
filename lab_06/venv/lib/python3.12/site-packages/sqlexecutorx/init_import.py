import importlib
from typing import Union
from .log_support import logger
from .support import InitArgs
from .error import DBError
from .constant import MYSQL_PORT, POSTGRESQL_PORT
from .engine import Engine, Driver, DRIVER_ENGINE_DICT


def import_driver(driver: Union[str, Driver], *args, **kwargs):
    creator = None
    if driver:
        driver_name = driver if isinstance(driver, str) else driver.value
        if driver_name in DRIVER_ENGINE_DICT:
            engine = DRIVER_ENGINE_DICT.get(driver_name)
        else:
            engine = Driver.UNKNOWN
            logger.warning(f"Driver '{driver_name}' not support yet, may be you should adapter it by yourself.")
        creator = do_import(driver_name, engine)
    else:
        curr_engine = get_engine(*args, **kwargs)
        drivers = dict(filter(lambda x: x[1] == curr_engine, DRIVER_ENGINE_DICT.items())) if curr_engine else DRIVER_ENGINE_DICT
        for driver_name, engine in drivers.items():
            try:
                creator = importlib.import_module(driver_name)
                break
            except ModuleNotFoundError:
                pass
        if not creator:
            raise DBError(f"You may forgot install driver, may be one of {list(DRIVER_ENGINE_DICT.keys())} suit you.")
    return engine, driver_name, creator


def do_import(driver_name, curr_engine):
    try:
        return importlib.import_module(driver_name)
    except ModuleNotFoundError:
        raise DBError(f"Import {curr_engine.value} driver '{driver_name}' failed, please sure it was installed or change other driver.")


def get_engine(*args, **kwargs):
    if args and isinstance(args[0], str):
        return _get_engine_from_url(args[0])
    elif InitArgs.PORT in kwargs:
        port = kwargs[InitArgs.PORT]
        if port == MYSQL_PORT:
            return Engine.MYSQL
        elif port == POSTGRESQL_PORT:
            return Engine.POSTGRESQL
    return None


def _get_engine_from_url(url: str):
    if 'mysql://' in url:
        return Engine.MYSQL
    elif 'postgres://' in url:
        return Engine.POSTGRESQL
    elif ':memory:' == url or '://' not in url:
        return Engine.SQLITE
