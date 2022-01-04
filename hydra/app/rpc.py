import argparse
import pprint
from functools import reduce

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

    def run(self):
        self.log.info(f"rpc: {self.args}")
        rpc = HydraRPC.__from_parsed__(self.args)

        call = getattr(rpc, self.args.call)

        try:
            result = call(*self.args.params)

            if self.args.json or self.args.json_pretty:

                print(result if not self.args.json_pretty else pprint.pformat(result))

            else:
                HydraRPCApp.render(self.args.call, result)

        except HydraRPC.Error as err:

            if log.level() <= log.INFO:
                raise

            print(err)
            exit(-1)

    @staticmethod
    def render(name, result, print_=print):
        if not isinstance(result, (list, dict)):
            print_(result)
            return

        flat = HydraRPCApp.flatten(name, result)

        spaces = lambda lvl: ""  # " " * lvl

        longest = max(len(v[0]) + len(spaces(v[2])) for (_, v) in flat.items()) + 4

        for label, value, level in flat.values():

            print_(f"{spaces(level)}{label}".ljust(longest) + (pprint.pformat(value) if value is not ... else ""))

    @staticmethod
    def flatten(name: str, result, level=0):
        lines = {name: [name, ..., level]}

        def _reduce(da, db):
            da.update(db)
            return da

        if isinstance(result, (list, dict)):
            lines.update(
                reduce(lambda da, db: _reduce(da, db), (
                        HydraRPCApp.flatten(f"{name}[{index}]", value, level=level + 1)
                        for (index, value) in enumerate(result)
                    ) if isinstance(result, list) else (
                        HydraRPCApp.flatten(f"{name}.{key}", value, level=level + 1)
                        for (key, value) in result.items()
                    ), {})
            )
        else:
            lines[name][1] = result

        return lines



if __name__ == "__main__":
    HydraRPCApp.main()
