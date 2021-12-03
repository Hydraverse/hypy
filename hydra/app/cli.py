import sys
import argparse

from hydra.app import HydraApp


@HydraApp.register(name="cli", desc="command-line interface", version="1.0")
class HydraCLIApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        pass

    def run(self):
        self.log.info("running!")
        print("printed stdout")
        print("printed stderr", file=sys.stderr)


if __name__ == "__main__":
    HydraCLIApp.main()
