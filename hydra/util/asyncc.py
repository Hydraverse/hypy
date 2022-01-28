"""Provide async versions of instance methods automatically.
"""
from typing import Callable
import asyncio
import inspect


class AsyncMethods:
    __instance: object

    def __init__(self, instance: object):
        self.__instance = instance

    @staticmethod
    async def __run_in_executor(fn: Callable, args: tuple, kwds: dict):
        return await asyncio.get_event_loop().run_in_executor(None, AsyncMethods.__executor_fn, fn, args, kwds)

    @staticmethod
    def __executor_fn(fn: Callable, args: tuple, kwds: dict):
        return fn(*args, **kwds)

    @staticmethod
    def __executor_callable(fn: Callable):
        async def await_fn(*args, **kwds):
            return await AsyncMethods.__run_in_executor(fn, args, kwds)

        return await_fn

    def __getattr__(self, attr: str):

        obj_attr = getattr(self.__instance, attr)

        if inspect.iscoroutinefunction(obj_attr):
            return obj_attr

        elif inspect.ismethod(obj_attr):
            return AsyncMethods.__executor_callable(obj_attr)

        return obj_attr
