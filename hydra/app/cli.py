import sys
import argparse
import pprint

from hydra.app import HydraApp
from hydra.rpc import HydraRPC
from hydra import log


@HydraApp.register(name="cli", desc="rpc cli interface", version="1.01")
class HydraRPCApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        HydraRPC.__parser__(parser, json_opt=True, pretty_opt=True)
        parser.add_argument("call", metavar="CALL", help="rpc function to call")
        parser.add_argument("params", nargs="*", type=HydraRPC.__parse_param__,
                            metavar="PARAM", help="rpc function parameters")
        parser.add_argument(
            "-f", "--full", action="store_true", help="output full names (non-json only)",
            default=False,
            required=False
        )

    def run(self):
        self.log.info(f"rpc: {self.args}")
        rpc = HydraRPC.__from_parsed__(self.args)

        call = getattr(rpc, self.args.call)

        try:
            result = call(*self.args.params)

            if self.args.json or self.args.json_pretty:
                print(str(result) if not self.args.json_pretty else pprint.pformat(result))

            else:
                spaces = (lambda lvl: "  " * lvl) if not self.args.full else lambda lvl: ""

                # for line in HydraRPC.Result.render(self.args.call, result, spaces=spaces, full=self.args.full):
                #     print(line)

                print("\n".join(
                    HydraRPC.Result.render(self.args.call, result, spaces=spaces, full=self.args.full)
                ))

        except HydraRPC.Error as err:

            if log.level() <= log.INFO:
                raise

            print(err)
            exit(-1)


if __name__ == "__main__":
    HydraRPCApp.main()
