"""TX input addresses.

Display the input and output addresses for a given transaction.
Requires `block_hash` when not using -txindex hydrad flag.
"""
import argparse

from hydra.app import HydraApp
from hydra.rpc import HydraRPC
from hydra.test import Test
from hydra import log


@HydraApp.register(name="txvio", desc=__doc__, version="1.01")
class TxVIOApp(HydraApp):
    assoc = {}

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument("txid", metavar="TXID", type=str, help="TX ID string")
        parser.add_argument("block_hash", metavar="BLOCK_HASH", type=str, nargs="?", default=None,
                            help="Block hash if known (required without -txindex)")

    def run(self):
        addresses_vin, addresses_vout = TxVIOApp.get_vinout_addresses(
            self.rpc, self.args.txid, self.args.block_hash
        )

        TxVIOApp.print_addresses(addresses_vin, addresses_vout)


    @staticmethod
    def print_addresses(addresses_vin: set, addresses_vout: set, indent: int = 0):

        addresses_vin, addresses_vout = list(addresses_vin), list(addresses_vout)

        base_len = 0

        for i in range(max(len(addresses_vin), len(addresses_vout))):

            if i < len(addresses_vin):
                if base_len == 0:
                    base_len = len(addresses_vin[i])

                line = " " * indent + addresses_vin[i]
            else:
                if base_len == 0:
                    base_len = len(addresses_vout[i])

                line = " " * (base_len + indent)

            if i < len(addresses_vout):
                line += ("    " if i != 0 else " -> ") + addresses_vout[i]

            print(line)

    @staticmethod
    def get_vinout_addresses(rpc, txid: str, block_hash: str = None) -> (set, set):
        rawtx = rpc.getrawtransaction(txid, False, block_hash)

        addresses_vin = set()
        addresses_vout = set()

        if len(rawtx):
            decoded = rpc.decoderawtransaction(rawtx, True)

            for vout in filter(lambda vout_: hasattr(vout_.scriptPubKey, "addresses"), decoded.vout):
                addresses_vout = addresses_vout.union(vout.scriptPubKey.addresses)

            for vin in filter(lambda vin_: hasattr(vin_, "txid"), decoded.vin):

                vin_rawtx = rpc.getrawtransaction(vin.txid, False)

                vin_rawtx_decoded = rpc.decoderawtransaction(vin_rawtx, True)

                vout = vin_rawtx_decoded.vout[vin.vout]

                if hasattr(vout.scriptPubKey, "addresses"):
                    addresses_vin = addresses_vin.union(vout.scriptPubKey.addresses)

                # print(f"{type(vin).__name__}:",
                #       str(vout.value).ljust(16, ' '),
                #       ", ".join(vout.scriptPubKey.addresses)
                # )

            return addresses_vin, addresses_vout


@Test.register()
class TxVIOAppTest(Test):

    def test_0_txvio_runnable(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(TxVIOApp, "-h")

    def test_1_txvio_run(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(
            TxVIOApp,
            "789d1aff68ff3eee189fbaa8119dbd024c5914b0a45904a08620b354b465cfaf",
            "cd9bd7b8914a4acaef7cfec1f93584845ff96f315f3edd48d41c9a4abb65f6cb"
        )

        self.assertHydraAppIsRunnable(
            TxVIOApp,
            "51182d9b97f6a9aabda5e5160719a6173e60b6a83e7650bfe54bc1361cac64e7"
        )


if __name__ == "__main__":
    TxVIOApp.main()
