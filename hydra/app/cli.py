import sys
import argparse
import pprint
import json

from hydra.app import HydraApp
from hydra.rpc import HydraRPC
from hydra import log


@HydraApp.register(name="cli", desc="rpc cli interface", version="1.01")
class HydraRPCApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument("call", metavar="CALL", help="rpc function to call")
        parser.add_argument("params", nargs="*", type=HydraRPC.__parse_param__,
                            metavar="PARAM", help="rpc function parameters")
        parser.add_argument(
            "-f", "--full", action="store_true", help="output full names (non-json only)",
            default=False,
            required=False
        )

    def run(self):
        rpc = self.rpc

        result = rpc.call(self.args.call, *self.args.params, raw=True)

        if self.args.json or self.args.json_pretty:
            print(json.dumps(result.__serialize__(name=self.args.call), indent=2 if self.args.json_pretty else None))

        else:
            result = result.Value

            spaces = (lambda lvl: "  " * lvl) if not self.args.full else lambda lvl: ""

            # for line in HydraRPC.Result.render(self.args.call, result, spaces=spaces, full=self.args.full):
            #     print(line)

            print("\n".join(
                HydraRPC.Result.render(self.args.call, result, spaces=spaces, full=self.args.full)
            ))


if __name__ == "__main__":
    HydraRPCApp.main()
