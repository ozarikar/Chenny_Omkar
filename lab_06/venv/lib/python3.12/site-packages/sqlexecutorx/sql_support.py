from functools import lru_cache
from typing import List, Tuple, Union
from .conf import lru_cache_size


def is_tuple_or_list(x):
    return isinstance(x, Tuple) or isinstance(x, List)


@lru_cache(maxsize=lru_cache_size)
def require_limit(sql: str):
    lower_sql = sql.lower()
    if 'limit' not in lower_sql:
        return True
    idx = lower_sql.rindex('limit')
    if idx > 0 and ')' in lower_sql[idx:]:
        return True
    return False


@lru_cache(maxsize=lru_cache_size)
def limit_sql(sql: str, placeholder: Union[str, int] = '?'):
    return f'{sql} LIMIT {placeholder}'

