from enum import Enum


class Engine(Enum):
    MYSQL = 'MySQL'
    POSTGRESQL = 'PostgreSQL'
    ORACLE = 'Oracle'
    SQL_SERVER = 'SQL Server'
    SQLITE = 'SQLite'
    UNKNOW = 'Unknow'


class Driver(Enum):
    MYSQL_CLIENT = 'MySQLdb'
    PYMYSQL = 'pymysql'
    MYSQL_CONNECTOR = 'mysql.connector'
    PSYCOPG2 = 'psycopg2'
    PG8000 = 'pg8000'
    PY_POSTGRESQL = 'postgresql.driver.dbapi20'
    PYGRESQL = 'pgdb'
    ORACLEDB = 'oracledb'
    SQLITE3 = 'sqlite3'


DRIVER_ENGINE_DICT = {
    Driver.MYSQL_CLIENT.value: Engine.MYSQL,
    Driver.PYMYSQL.value: Engine.MYSQL,
    Driver.MYSQL_CONNECTOR.value: Engine.MYSQL,
    Driver.PSYCOPG2.value: Engine.POSTGRESQL,
    Driver.PG8000.value: Engine.POSTGRESQL,
    Driver.PY_POSTGRESQL.value: Engine.POSTGRESQL,
    Driver.PYGRESQL.value: Engine.POSTGRESQL,
    Driver.ORACLEDB.value: Engine.ORACLE,
    Driver.SQLITE3.value: Engine.SQLITE
}