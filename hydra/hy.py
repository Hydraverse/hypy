"""HyPy Library Application Tool.
"""
from __future__ import annotations
import sys
import os
import argparse
import argcomplete

from hydra.app import HydraApp
from hydra import log


class Hydra:
    args: argparse.Namespace = None
    __main: Hydra = None
    __app: HydraApp = None

    def __init__(self, args):
        self.args = args

    def __getstate__(self):
        return self.args

    def __setstate__(self, state):
        self.args = state

    def run(self):

        info = HydraApp.get(self.args.app)

        log.debug(f"app {info.name} ...")

        app = self.__app = HydraApp.make(info, hy=self)

        if app is not None:
            return app.run()

    @property
    def app(self) -> HydraApp:
        return self.__app

    @staticmethod
    def get() -> Hydra:
        """Get the current Hydra instance running the main app.
        """
        return Hydra.__main

    @staticmethod
    def main(name=None):
        if name is not None:
            sys.argv[0] = f"hy-{name}"
        else:
            sys.argv[0] = "hy"

        app, basename, app_has_arg = Hydra.__global_app()

        parser = Hydra.__parser(app, basename, app_has_arg)
        argcomplete.autocomplete(parser)
        args = parser.parse_args()

        if app:
            args.app = app.name

        log.log_config(args)

        # noinspection PyBroadException
        try:
            hy = Hydra.__main = Hydra(args)

            hy.run()

        except KeyboardInterrupt:
            print(file=sys.stderr)
            sys.exit(0)

        except Exception as exc:
            log.critical(f"hy: {exc}")

            if args.verbose:
                raise

            sys.exit(-1)

    @staticmethod
    def __parser(app, basename, app_has_arg):
        parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), description=__doc__)

        def raise_if_no_match(a):
            if app and a != basename:
                raise argparse.ArgumentTypeError(f"{a} != {basename}")
            return a

        if app:
            if app_has_arg:
                parser.add_argument("app", type=raise_if_no_match, metavar=basename,
                                    help=app.desc, choices=HydraApp.APPS)

            Hydra.__parser_base(parser, app)

            app_pg = parser.add_argument_group(title=app.name, description=app.desc)

            app.cls.parser(app_pg)

        else:
            parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

            subparsers = parser.add_subparsers(
                dest="app", title="applications", help="application to run", metavar="APP", required=True
            )

            for app in HydraApp.all():
                app_p = subparsers.add_parser(app.name, aliases=app.aliases, help=app.desc)

                Hydra.__parser_base(app_p, app)

                app_pg = app_p.add_argument_group(title=app.name, description=app.desc)

                app.cls.parser(app_pg)

        return parser

    @staticmethod
    def __parser_base(parser, app=None):

        if app is not None and app.version:
            parser.add_argument(f'-V', f'--version', action='version', version=f'hy-{app.name} {app.version}')

        log.log_parser(parser)

        HydraApp.parser(parser)

    @staticmethod
    def __parser_global():
        parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), description=__doc__)
        parser.add_argument("app", help="application to run.", choices=HydraApp.APPS)
        Hydra.__parser_base(parser)
        parser.add_argument("args", default=[], nargs=argparse.REMAINDER,
                            metavar="ARGS", help="application args.")

        return parser

    @staticmethod
    def __global_app():
        base = os.path.basename(sys.argv[0])

        if base.startswith("hy-"):
            name = sys.argv[0].split("-", 1)[1]
            return HydraApp.get(name), name, False

        if base != "hy":
            name = os.path.splitext(base)[0]
            return HydraApp.get(name), name, False

        # Load a parser and run it to determine app.
        parser = Hydra.__parser_global()
        argcomplete.autocomplete(parser)
        args = parser.parse_args()

        return HydraApp.get(args.app), args.app, True

    @staticmethod
    def slice_type(slce):
        if ":" not in slce:
            raise argparse.ArgumentTypeError("slice has no colon.")

        split = slce.split(":", 2)

        step = ""

        if len(split) == 3:
            begin, end, step = split
        else:
            begin, end = split

        begin = 0 if not len(begin) else int(begin)
        end = sys.maxsize if not len(end) else int(end)
        step = 1 if not len(step) else int(step)

        return range(begin, end, step)

    @staticmethod
    def slice_arg(parser, *args, **kwds):
        parser.add_argument(
            *args,
            metavar="[B]:[E][:S]",
            type=Hydra.slice_type,
            default=None,
            **kwds
        )

    @staticmethod
    def arg_env_or_req(key):
        """Return for argparse "default=os.environ[key]" if set else required=True
        """
        return dict(default=os.environ.get(key)) if os.environ.get(key) else dict(required=True)

    @staticmethod
    def arg_env_or_none(key, default=None):
        """Return for argparse "default=os.environ[key]" if set else default=None
        """
        return dict(default=os.environ.get(key, default))


if __name__ == "__main__":
    Hydra.main()
