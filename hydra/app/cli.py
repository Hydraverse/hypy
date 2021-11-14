import sys
import argparse

from hydra.app import HydraApp


@HydraApp.register(name="cli", desc="command-line interface")
class HydraCLIApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

    def run(self):
        self.log.info("running!")
        print("printed stdout")
        print("printed stderr", file=sys.stderr)


if __name__ == "__main__":
    HydraCLIApp.main()
