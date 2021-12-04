"""Hydra Applications.
"""
import sys
import argparse
import importlib

from hydra import log
from hydra.util.struct import dictuple, namedtuple


APPS = "cli", "rpc", "test", "ascan", "lstx", "txvio"

__all__ = "HydraApp", "APPS"


__INFO__ = {}


MethodInfo = namedtuple("Info", ("name", "desc", "cls", "aliases", "version"))


class HydraApp:
    """Base class for all Hydra applications.
    """
    hy = None
    args = None
    log = None

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

        self.args = dictuple("args", self.args)

        super().__init__()

        if self.__class__.setup is not HydraApp.setup:
            self.__setup = self.setup
            self.setup = self.__auto_setup_fail
            self.__run = self.run
            self.run = self.__auto_setup_run

    def __auto_setup_run(self, *args, **kwds):
        self.__setup()
        return self.__run(*args, **kwds)

    def __auto_setup_fail(self, *args, **kwds):
        raise RuntimeError("direct calls to setup() disallowed.")

    def __getstate__(self):
        return self.hy, self.args, self.log

    def __setstate__(self, state):
        self.hy, self.args, self.log = state

    # @property
    # def info(self) -> MethodInfo:
    #     for info in __INFO__.values():
    #         if info.cls == self.__class__:
    #             return info
    #
    #     raise ModuleNotFoundError

    def setup(self):
        return self.__auto_setup_fail()

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
        pass

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
