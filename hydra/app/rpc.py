import sys
import argparse

from hydra.app import HydraApp


@HydraApp.register(name="rpc", desc="rpc interface")
class HydraRPCApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

    def run(self):
        self.log.info(f"rpc: args={self.args}")


if __name__ == "__main__":
    HydraRPCApp.main()
