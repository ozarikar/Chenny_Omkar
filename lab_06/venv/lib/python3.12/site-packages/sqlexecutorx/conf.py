import os
from .constant import CACHE_SIZE

lru_cache_size = int(os.getenv('LRU_CACHE_SIZE', CACHE_SIZE))
