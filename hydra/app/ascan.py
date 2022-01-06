"""Address scanner.

Search transactions for all addresses used as inputs to TXes from this address.
"""
import os.path
import sys
import argparse

from hydra.app.cli import HydraApp
from hydra.test import Test
from hydra.hy import Hydra

from .txvio import TxVIOApp


@HydraApp.register(name="ascan", desc=__doc__, version="1.01")
class AScanApp(HydraApp):
    out = None

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument("-c", "--count", type=int, default=10, help="number of recent transactions to load")
        parser.add_argument("-s", "--skip", type=int, default=0, help="number of recent transactions to skip")
        parser.add_argument("-R", "--recursive", action="store_true", help="scan vin addresses recursively")
        parser.add_argument("-o", "--output",  help="also output to a file (use {} for address in name)")
        parser.add_argument("-a", "--append", action="store_true", help="load addresses from and append to output file")
        parser.add_argument("address", metavar="ADDR", type=str, help="address to scan")

    def run(self):
        address = self.args.address
        addresses = set()

        if self.args.output:
            filename = self.args.output.replace("{}", address)

            if self.args.append and os.path.isfile(filename):

                with open(filename, "r") as file:
                    for line in file.readlines():
                        addr_src, addr_vin = line.strip().split(": ")
                        addresses.update((addr_vin,))
                        address = addr_vin

            self.out = open(filename, "a")

        for (addr_scan, addr_found) in AScanApp.ascan(self.rpc, address, self.args.count, self.args.skip,
                                                      addr_found=addresses,
                                                      recursive=self.args.recursive):
            line = f"{addr_scan}: {addr_found}\n"
            print(line, end="")
            sys.stdout.flush()

            if self.out is not None:
                self.out.write(line)
                self.out.flush()

    @staticmethod
    def ascan(rpc, address, count: int, skip: int = None, addr_found: set = None, recursive=False):
        if addr_found is None:
            addr_found = set()

        logs = Hydra.get().app.log

        if not rpc.validateaddress(address).isvalid:
            raise ValueError(f"{address}: invalid address")

        logs.info(f"{address}: importing address...")
        rpc.importaddress(address=address, label=address)

        logs.info(f"{address}: getting transactions...")
        txns = rpc.listtransactions(
            label=address, count=count, skip=skip,
            include_watchonly=True
        )

        logs.info(f"{address}: scanning {len(txns)} TXes for vin addresses...")
        for txn in txns:
            logs.debug(f"{address}: txid: {txn.txid}")
            addr_vin, addr_vout = TxVIOApp.get_vinout_addresses(rpc, txn.txid, txn.blockhash)
            logs.debug(f"{address}: addr: vin={addr_vin} vout={addr_vout}")

            if address in addr_vin:
                addrs_vin_union = addr_found.union(addr_vin)
                addrs_vin_diff = addrs_vin_union.difference(addr_found)
                addr_found.update(addrs_vin_union)

                for addr in addrs_vin_diff:

                    yield address, addr

                    if recursive and addr != address:
                        for (r_addr_scan, r_addr_found) in AScanApp.ascan(rpc, addr, count, skip, addr_found, recursive):
                            yield r_addr_scan, r_addr_found


@Test.register()
class AScanAppTest(Test):

    def test_0_ascan_runnable(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(AScanApp, "-h")

    def test_1_ascan_run(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(AScanApp, "--rpc-wallet=watch", "HVknEFy1R2mfuegku1S7bMwpHLjoqVGJxF")


if __name__ == "__main__":
    AScanApp.main()
