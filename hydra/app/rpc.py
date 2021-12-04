import argparse

from hydra.app import HydraApp
from hydra.rpc import HydraRPC
from hydra import log


@HydraApp.register(name="rpc", desc="rpc interface", version="1.01")
class HydraRPCApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        HydraRPC.__parser__(parser)
        parser.add_argument("call", metavar="CALL", help="rpc function to call")
        parser.add_argument("params", nargs="*", type=HydraRPC.__parse_param__,
                            metavar="PARAM", help="rpc function parameters")

    def run(self):
        self.log.info(f"rpc: {self.args}")
        rpc = HydraRPC.__from_parsed__(self.args)

        call = getattr(rpc, self.args.call)

        try:
            result = call(*self.args.params)

            print(rpc.__string__(result))

        except HydraRPC.Error as err:

            if log.level() <= log.INFO:
                raise

            print(err)
            exit(-1)


if __name__ == "__main__":
    HydraRPCApp.main()
