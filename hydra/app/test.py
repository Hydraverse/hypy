import sys
import argparse

from hydra.app import HydraApp


@HydraApp.register(name="test", desc="test interface")
class HydraTestApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')
        parser.add_argument('target', default="-", metavar='TARGET', help='test target or "-" to skip.')
        parser.add_argument('args', default=[], nargs=argparse.REMAINDER, metavar='ARGS', help='test args.')

    def run(self):
        sys.argv = sys.argv[:1] + ([] if self.args.target == '-' else [self.args.target]) + list(self.args.args)
        self.log.debug(f"test: argv={sys.argv}")
        # noinspection PyUnresolvedReferences
        from hydra.test import __main__


if __name__ == "__main__":
    HydraTestApp.main()
