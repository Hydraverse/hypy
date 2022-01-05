import sys
import os
import argparse
import importlib.util

from hydra.app import HydraApp


@HydraApp.register(name="test", desc="test interface", version="1.0")
class HydraTestApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument("target", default="-", metavar="TARGET", help="test target or '-' to skip.")
        parser.add_argument("args", default=[], nargs=argparse.REMAINDER,
                            metavar="ARGS", help="test args.")

    def run(self):
        # For convenience, same as passing file name after dash.
        if os.path.isfile(self.args.target):
            sys.argv[1] = os.path.splitext(os.path.basename(self.args.target))[0]
            spec = importlib.util.spec_from_file_location(sys.argv[1], self.args.target)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

        sys.argv = sys.argv[:1] + ([] if self.args.target == "-" else [self.args.target])
        self.log.debug(f"test: argv={sys.argv}")

        from hydra.test import Test

        # Ensure internal tests are loaded
        # noinspection PyUnresolvedReferences
        import hydra.test.tests

        # Ensure internal app tests are loaded
        HydraApp.all()

        Test.main(self.args.args)


if __name__ == "__main__":
    HydraTestApp.main()
