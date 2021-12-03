"""HyPy Library Application Tool.
"""
import sys
import os
import argparse
import argcomplete

from hydra.app import HydraApp
from hydra import log


class Hydra:
    args: argparse.Namespace = None

    def __init__(self, args):
        self.args = args

    def __getstate__(self):
        return self.args

    def __setstate__(self, state):
        self.args = state

    def run(self):

        info = HydraApp.get(self.args.app)

        log.debug(f"app {info.name} ...")

        app = HydraApp.make(info, hy=self)

        if app is not None:
            return app.run()

    @staticmethod
    def main(name=None):
        if name is not None:
            sys.argv[0] = f"hy-{name}"
        else:
            sys.argv[0] = "hy"

        parser = Hydra.parser()
        argcomplete.autocomplete(parser)
        args = parser.parse_args()

        app = Hydra.global_app()

        if app:
            args.app = app.name

        log.log_config(args)

        # noinspection PyBroadException
        try:
            hy = Hydra(args)

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
    def parser():
        parser = argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), description=__doc__)
        parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

        app = Hydra.global_app()

        if app:
            Hydra.__parser_base(app, parser)

            app_pg = parser.add_argument_group(title=app.name, description=app.desc)

            app.cls.parser(app_pg)

        else:
            subparsers = parser.add_subparsers(
                dest="app", title="applications", help="application to run", metavar="APP"
            )

            subparsers.required = True  # TODO: Move to keyword arg for Python 3.7

            for app in HydraApp.all():
                app_p = subparsers.add_parser(app.name, aliases=app.aliases, help=app.desc)

                Hydra.__parser_base(app, app_p)

                app_pg = app_p.add_argument_group(title=app.name, description=app.desc)

                app.cls.parser(app_pg)

        return parser

    @staticmethod
    def __parser_base(app, parser):

        parser_main = parser.add_argument_group(title="primary arguments")

        if app.version:
            parser_main.add_argument('-V', f'--version-{app.name}', action='version', version=f'hy-{app.name} {app.version}')

        log.log_parser(parser_main)

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
    def global_app():
        base = os.path.basename(sys.argv[0])

        if base.startswith("hy-"):
            return HydraApp.get(sys.argv[0].split("-", 1)[1])

        if base != "hy":
            return HydraApp.get(os.path.splitext(base)[0])

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
