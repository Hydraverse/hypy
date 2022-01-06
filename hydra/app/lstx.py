"""List transactions for a block range.

Display the transactions within the given range of blocks.
"""
import argparse
import json

from hydra.app.cli import HydraApp
from hydra.rpc import HydraRPC
from hydra.test import Test

from .txvio import TxVIOApp


@HydraApp.register(name="lstx", desc=__doc__, version="1.01")
class TxListApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument("-a", "--addrs", action="store_true", default=False, required=False,
                            help="also print TX input & output addresses")
        parser.add_argument("block_from", metavar="FROM", type=int,
                            help="block index offset relative to current block height, or 0 for first")
        parser.add_argument("block_to", metavar="TO", type=int, nargs="?", default=0,
                            help="block index relative to current block height, default latest")

    def run(self):
        block_count = self.rpc.getblockcount()

        block_from = self.args.block_from if self.args.block_from == 0 else (
                block_count + self.args.block_from if self.args.block_from < 0 else self.args.block_from
        )

        block_to = (block_count if block_from <= 0 else block_from) if self.args.block_to == 0 else (
                block_count + self.args.block_to if self.args.block_to < 0 else self.args.block_to
        )

        if block_from > block_to:
            raise argparse.ArgumentError(self.args.block_from, "block_from must be <= block_to")

        block_tx = TxListApp.get_block_range_tx(self.rpc, block_from, block_to)

        for height, (block_hash, txes) in block_tx.items():
            print(str(height).ljust(7, " "), block_hash)

            if not self.args.addrs:
                print("\n".join(" " * 8 + txid for txid in txes))
            else:
                for txid in txes:
                    print(" " * 8 + txid)
                    addrs_vin, addrs_vout = TxVIOApp.get_vinout_addresses(self.rpc, txid, block_hash)
                    TxVIOApp.print_addresses(addrs_vin, addrs_vout, 12)

    @staticmethod
    def get_block_range_tx(rpc: HydraRPC, height_from: int, height_to: int) -> dict:
        block_tx = {}

        for height in range(height_from, height_to + 1):
            block_hash = TxListApp.get_block_hash(rpc, height)
            txes = TxListApp.get_block_tx(rpc, block_hash)

            if len(txes):
                block_tx[height] = block_hash, txes

        return block_tx

    @staticmethod
    def get_block_hash(rpc: HydraRPC, height: int) -> str:
        return rpc.getblockstats(height).blockhash

    @staticmethod
    def get_block_tx(rpc: HydraRPC, block_hash: str) -> list:
        block = rpc.getblock(block_hash)

        return block.tx if block.nTx > 0 else []


@Test.register()
class TxListAppTest(Test):

    def test_0_lstx_runnable(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(TxListApp, "-h")

    def test_1_lstx_run(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(TxListApp, "--rpc-wallet=watch", "-a", "1337")


if __name__ == "__main__":
    TxListApp.main()
