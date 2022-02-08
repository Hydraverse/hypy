"""Hydra Applications.
"""
import argparse
import importlib
import json

import os
from collections import namedtuple
from attrdict import AttrDict

from hydra import log
from hydra.rpc import BaseRPC, HydraRPC


APPS = "cli", "test", "ascan", "atrace", "call", "lstx", "txvio", "peerscan", "top"

__all__ = "HydraApp", "APPS"


__INFO__ = {}


MethodInfo = namedtuple("Info", ("name", "desc", "cls", "aliases", "version"))


class HydraApp:
    """Base class for all Hydra applications.
    """
    APPS = APPS

    hy = None
    args = None
    log = None
    rpc = None
    __run = None

    # noinspection PyProtectedMember
    def __init__(self, *, hy=None, **kwds):
        self.hy = hy
        self.args = kwds
        self.log = log

        if self.hy is not None:
            self.args.update(vars(self.hy.args))

        else:
            import argparse

            info = self.info

            parser = argparse.ArgumentParser()

            info.cls.parser(parser)

            for action in parser._actions:
                if action.dest is not argparse.SUPPRESS:
                    if action.dest not in self.args:
                        if action.required:
                            raise ValueError(f"argument '{action.dest}' is required for {info.name} application.")
                        elif action.default is not argparse.SUPPRESS:
                            self.args[action.dest] = action.default

            for dest in parser._defaults:
                if not dest not in self.args:
                    self.args[dest] = parser._defaults[dest]

        self.args = AttrDict(self.args)

        if not os.getenv("HYPY_NO_RPC_ARGS", False):
            self.rpc = HydraRPC.__from_parsed__(self.args)

        super().__init__()

        self.__run = self.run
        self.run = self.__auto_setup_run

    def __auto_setup_run(self, *args, **kwds):
        self.setup()

        try:
            return self.__run(*args, **kwds)

        except BaseRPC.Exception as err:

            if log.level() <= log.INFO:
                raise

            if self.args.json:
                print(json.dumps(err.error or err.response, default=str, indent=2 if self.args.json_pretty else None))
            else:
                self.render(err.error, "error")
            exit(-1)

    def __auto_setup_fail(self, *args, **kwds):
        raise RuntimeError("direct calls to setup() disallowed.")

    def __getstate__(self):
        return self.hy, self.args, self.log

    def __setstate__(self, state):
        self.hy, self.args, self.log = state

    def render(self, result: [dict, object], name: str, print_fn=print, ljust=None):
        """Render a result.
        """
        if self.args.get("json", False) or self.args.get("json_pretty", False):
            print_fn(json.dumps(
                result,
                default=str,
                indent=2 if self.args.get("json_pretty", False) else None
            ))

        else:
            full = self.args.get("full", False)
            spaces = (lambda lvl: "  " * lvl) if not full else lambda lvl: ""

            if self.args.get("unbuffered", False):
                for line in HydraApp.render_yield(result=result, name=name, spaces=spaces, full=full, longest=ljust):
                    print_fn(line)
            else:
                print_fn("\n".join(
                    HydraApp.render_yield(result=result, name=name, spaces=spaces, full=full, longest=ljust)
                ))

    @staticmethod
    def render_yield(result, name: str, spaces=lambda lvl: "  " * lvl, longest: int = None, full: bool = False):
        if not isinstance(result, (list, tuple, dict)):
            yield str(result)
            return

        flat = HydraApp.flatten(name, result, full=full)

        if not longest:
            flat = list(flat)
            longest = max(len(row[0]) + len(spaces(row[2])) for row in flat) + 4

        for label, value, level in flat:
            yield f"{spaces(level)}{label}".ljust(longest) \
                  + (str(value) if value is not ... else "")

    @staticmethod
    def flatten(name: str, result, level: int = 0, full: bool = False) -> dict:
        if not isinstance(result, (list, tuple, dict)):
            yield name, result, level
            return

        yield name, ..., level

        if not isinstance(result, dict):
            for index, value in enumerate(result):
                yield from HydraApp.flatten(
                    (name if full else "")  # name.rsplit(".", 1)[0] if "." in name else name)
                    + f"[{index}]", value, level=level + 1, full=full
                )
        else:
            for key, value in result.items():
                yield from HydraApp.flatten(
                    (name if full else "") + f".{key}", value, level=level + 1, full=full
                )

    def setup(self):
        if self.args.json_pretty:
            self.args.json = True

    def run(self, *args, **kwds):
        raise NotImplementedError

    @staticmethod
    def make(info, *, hy=None, **kwds):
        # assert isinstance(info.cls, HydraApp.__class__)
        return info.cls(hy=hy, **kwds)

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        """Add method parameters to the argument parser.
        """
        if not os.getenv("HYPY_NO_RPC_ARGS", False):
            HydraRPC.__parser__(parser)

        if not os.getenv("HYPY_NO_JSON_ARGS", False):

            parser.add_argument(
                "-J", "--json-pretty", action="store_true", help="output parseable json",
                default=False,
                required=False
            )

            parser.add_argument(
                "-j", "--json", action="store_true", help="output parseable json",
                default=False,
                required=False
            )

            parser.add_argument(
                "-f", "--full", action="store_true", help="output full names (non-json only)",
                default=False,
                required=False
            )

    @staticmethod
    def __new_entry(cls, name, desc="", aliases=None, version=None):
        cls.info = MethodInfo(name=name, desc=desc, cls=cls, aliases=aliases or [], version=version)
        cls.main = staticmethod(lambda: HydraApp.main(cls.info.name))
        __INFO__[name] = cls.info
        return cls

    @staticmethod
    def register(*, name, desc="", aliases=None, version=None):  # TODO: support the aliases (????)
        def hook(cls):
            return HydraApp.__new_entry(cls, name, desc, aliases, version)

        return hook

    @staticmethod
    def get(name, default=None):
        HydraApp.__import(name)
        return __INFO__.get(name, default)

    @staticmethod
    def __import(name):
        """Attempt to import component module.

        This will fail for non-hydra modules when apps are run as standalone.
        """
        try:
            importlib.import_module(f"hydra.app.{name}")
        except ImportError:
            pass

    @staticmethod
    def all():
        for app in APPS:
            HydraApp.__import(app)

        return __INFO__.values()

    @staticmethod
    def main(name=None):
        from hydra.hy import Hydra

        Hydra.main(name)
