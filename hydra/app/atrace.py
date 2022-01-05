"""Address tracer.

Search transactions recursively to determine original funding source for an address.
"""
import os.path
import sys
import math
import argparse
from datetime import datetime

from hydra.app.cli import HydraApp
from hydra.rpc import HydraRPC
from hydra.test import Test

from .txvio import TxVIOApp


@HydraApp.register(name="atrace", desc=__doc__, version="1.01")
class ATraceApp(HydraApp):
    out = None

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument("-c", "--count", type=int, default=1000000,
                            help="max number of recent transactions to load")
        parser.add_argument("address", metavar="ADDR", type=str, help="address to trace")

    def run(self):
        address = self.args.address
        blocktime = 2**32
        amount = 0
        vins = set()

        try:
            self.rpc.getaddressesbylabel(label=address)
        except HydraRPC.Exception as err:
            pass  # TODO: Check that err is label not found: error(code=-11, ...)
            self.log.info(f"{address}: importing")
            self.rpc.importaddress(address=address, label=address, rescan=True)

        txns = self.rpc.listtransactions(label=address, count=self.args.count, skip=0, include_watchonly=True)

        self.log.info(f"{address}: scanning {len(txns)} transactions")

        for txn in txns:
            if txn.amount > 0 and txn.blocktime <= blocktime:
                (addr_vin, addr_vout) = TxVIOApp.get_vinout_addresses(self.rpc, txn.txid, txn.blockhash)

                if address in addr_vout and address not in addr_vin:
                    if len(addr_vin):
                        self.log.info(f"{address}: tx {datetime.fromtimestamp(txn.blocktime)} vins={addr_vin}")
                        blocktime = txn.blocktime
                        vins = addr_vin
                        amount = txn.amount
                    else:
                        # Get contract address from vout
                        txd = self.rpc.decoderawtransaction(
                            hexstring=self.rpc.getrawtransaction(txn.txid, False, txn.blockhash),
                            iswitness=True
                        )

                        for vout in filter(lambda vout_: not hasattr(vout_.scriptPubKey, "addresses"), txd.vout):
                            # NOTE: Only works for testnet faucet OP_CALL,
                            #       mainnet asm[-2] == OP_RETURN (Coinbase input)
                            asm = vout.scriptPubKey.asm.split()
                            self.log.info(
                                f"{address}: tx {datetime.fromtimestamp(txn.blocktime)} op={asm[-1]} addr={asm[-2]}"
                            )
                            blocktime = txn.blocktime
                            vins = {asm[-2]}
                            amount = txn.amount

        print(f"{address}: {','.join(vins)} {datetime.fromtimestamp(blocktime)} {amount}")


@Test.register()
class ATraceAppTest(Test):

    def test_0_atrace_runnable(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(ATraceApp, "-h")

    def test_1_atrace_run(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(ATraceApp, "-w watch", "HVknEFy1R2mfuegku1S7bMwpHLjoqVGJxF")


if __name__ == "__main__":
    ATraceApp.main()
