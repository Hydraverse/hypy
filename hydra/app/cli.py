import sys
import argparse

from hydra.app import HydraApp
from hydra.rpc import HydraRPC, ExplorerRPC


@HydraApp.register(name="cli", desc="rpc cli interface", version="1.01")
class HydraCLIApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-u", "--unbuffered", action="store_true", help="render output per-line (non-json only)",
            default=False,
            required=False
        )

        parser.add_argument("call", metavar="CALL", help="rpc function to call")
        parser.add_argument("params", nargs="*", type=HydraRPC.__parse_param__,
                            metavar="PARAM", help="rpc function parameters")

    def run(self):
        rpc = self.rpc
        call: str = self.args.call

        if call.startswith("x."):
            xrpc = ExplorerRPC(mainnet=rpc.mainnet)
            call = call.replace("x.", "", 1)
            result = xrpc.call(call, *self.args.params)
        else:
            result = rpc.call(call, *self.args.params, raw=True)

        self.render(result=result, name=call, print_fn=self.print_fn)

    def print_fn(self, line: str):
        print(line)

        if self.args.unbuffered:
            sys.stdout.flush()


if __name__ == "__main__":
    HydraCLIApp.main()
