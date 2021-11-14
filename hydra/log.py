"""Logging.
"""
import sys
import os
import argparse
import logging
from logging import *

__all__ = (
    "log_parser",
    "log_config",
    "log_set",
    "printl",
    "printle",
    "log",
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    "fatal",
    "exception",
    "shutdown",
)

LEVELS = (ERROR, WARNING, INFO, DEBUG)


for name, level in logging._nameToLevel.items():
    globals()[name] = level
    __all__ = __all__ + (name, )

__level = NOTSET


def level():
    return __level


def log_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=int(os.environ.get("HYPY_V", "0")),
        help="verbose level (up to 3x) (env: HYPY_V)."
    )

    parser.add_argument(
        "-l", "--log",
        type=lambda p: logging._nameToLevel[p.upper()],
        default=logging._nameToLevel[os.environ.get("HYPY_LOG", "NOTSET")],
        help="log level (name: error,warning,info,debug,notset) (env: HYPY_LOG)."
    )


def log_set(levl):
    global __level
    __level = levl
    return logging.root.setLevel(__level)


def log_config(args=None, default=None):
    global __level

    __level = NOTSET

    if "HYPY_V" in os.environ or "HYPY_LOG" in os.environ:
        verbose = int(os.environ.get("HYPY_V", "0"))
        __level = os.environ.get("HYPY_LOG", "NOTSET")

        __level = LEVELS[min(len(LEVELS) - 1, verbose)] if __level == "NOTSET" else logging._nameToLevel[__level]

    elif default is not None:
        __level = default

    if args is not None and __level == NOTSET:
        __level = args.log if args.log != NOTSET else LEVELS[min(len(LEVELS) - 1, args.verbose)]

    logging.root.name = "hypy"
    return log_set(__level)


__print = print


# noinspection PyShadowingBuiltins
def print(*args, **kwds):
    if __level >= NOTSET:
        return __print(*args, **kwds)


def printd(*args, **kwds):
    if __level <= DEBUG:
        return __print(*args, **kwds)


def printl(*args, **kwds):
    if __level <= INFO:
        return printd(*args, **kwds)


def printle(*args, **kwds):
    if __level <= WARNING:
        return printl(*args, **kwds, file=sys.stderr)


log_config()
