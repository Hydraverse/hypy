from collections import defaultdict
from datetime import datetime, timedelta
from functools import lru_cache
from typing import TypeVar, Generic, DefaultDict, Callable

CacheKeyType = TypeVar("CacheKeyType")
CacheValType = TypeVar("CacheValType")


class TimedLRU(Generic[CacheKeyType, CacheValType]):
    expiry: timedelta

    _cache: Callable[[CacheKeyType], CacheValType]
    _time: DefaultDict[CacheKeyType, datetime]

    def __init__(self, expiry: timedelta, cache: Callable[[CacheKeyType], CacheValType]):
        self.expiry = expiry
        self._cache = cache
        self._time = defaultdict(lambda: datetime.now())

    def __time(self, key: CacheKeyType) -> datetime:
        time = self._time[key]
        now = datetime.now()

        expired = (now - time) >= self.expiry

        return now if expired else time

    @lru_cache(maxsize=None)
    def get(self, key: CacheKeyType, time: datetime) -> CacheValType:
        val: CacheValType = self._cache(key)
        self._time[key] = time
        return val

    def __getitem__(self, key: CacheKeyType):
        return self.get(
            key=key,
            time=self.__time(key)
        )

    def __delitem__(self, key: CacheKeyType):
        del self._time[key]
