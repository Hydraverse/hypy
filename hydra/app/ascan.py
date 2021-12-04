"""Address scanner.

Search transactions for all addresses used as inputs to TXes from this address.
"""
import argparse

from hydra.app.rpc import HydraRPCApp, HydraApp
from hydra.rpc import HydraRPC
from hydra.test import Test
from hydra import log

from .txvio import TxVIOApp


@HydraApp.register(name="ascan", desc=__doc__, version="1.01")
class AScanApp(HydraRPCApp):
    rpc = None

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        HydraRPC.__parser__(parser, allow_json=False)
        parser.add_argument("-c", "--count", type=int, default=10, help="number of recent transactions to load")
        parser.add_argument("-s", "--skip", type=int, default=0, help="number of recent transactions to skip")
        parser.add_argument("address", metavar="ADDR", type=str, help="address to scan")

    def run(self):
        self.log.info(f"ascan: {self.args}")

        self.rpc = HydraRPC.__from_parsed__(self.args)

        addrs_vin = set()

        try:
            if not self.rpc.validateaddress(self.args.address).isvalid:
                raise argparse.ArgumentError(self.args.address, "invalid address")

            self.log.info("importing address...")
            self.rpc.importaddress(address=self.args.address, label=self.args.address)

            self.log.info("getting transactions...")
            txns = self.rpc.listtransactions(
                label=self.args.address, count=self.args.count, skip=self.args.skip,
                include_watchonly=True
            )

            self.log.info("scanning tx vin addresses...")
            for txn in txns:
                self.log.debug(f"txid: {txn.txid}")
                addr_vin, addr_vout = TxVIOApp.get_vinout_addresses(self.rpc, txn.txid, txn.blockhash)
                self.log.debug(f"addr: {addr_vin} {addr_vout}")

                if self.args.address in addr_vin:
                    addrs_vin_union = addrs_vin.union(addr_vin)
                    addrs_vin_diff = addrs_vin_union.difference(addrs_vin)
                    addrs_vin = addrs_vin_union

                    if len(addrs_vin_diff):
                        print("\n".join(addrs_vin_diff))

        except HydraRPC.Error as err:

            if log.level() <= log.INFO:
                raise

            print(err)
            exit(-1)


@Test.register()
class AScanAppTest(Test):

    def test_0_ascan_runnable(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(AScanApp, "-h")

    def test_1_ascan_run(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(AScanApp, "TvuuV8G8S3dstJ6C75WJLPKboiA4qX8zNv")


if __name__ == "__main__":
    AScanApp.main()
