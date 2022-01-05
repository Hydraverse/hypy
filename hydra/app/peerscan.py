#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
from argparse import ArgumentParser

from hydra.app import HydraApp
from hydra.rpc import HydraRPC
from hydra.test import Test

import re


@HydraApp.register(name="peerscan", desc="Connect to new nodes", version="1.1")
class PeerScan(HydraApp):

    @staticmethod
    def parser(parser: ArgumentParser):
        parser.add_argument("-c", "--count", type=int, default=10000, help="number of addresses to try")

    def run(self):
        self.log.info(f"server reports {self.rpc.getconnectioncount()} connections")

        peers = self.rpc.getpeerinfo()
        addrs = []

        for peer in peers:
            match = re.match(r"\[(.+)]:(\d+)", peer.addr)

            if not match:
                match = re.match(r"(\d+\.\d+\.\d+\.\d+)(?::(\d+))?", peer.addr)

            addr = match.group(1) if match else peer.addr

            addrs.append(addr)

        self.log.info(f"loaded {len(peers)} peers")

        nodes = self.rpc.getnodeaddresses(self.args.count)

        self.log.info(f"loaded {len(nodes)} nodes")

        nodes_add = [(node.address, node.port) for node in filter(lambda n: n.address not in addrs, nodes)]

        self.log.info(f"trying {len(nodes_add)} potential new peers")

        for addr, port in nodes_add:

            addr = f"{addr}:{port}" if ":" not in addr else f"[{addr}]:{port}"
            (self.log.debug if port != HydraRPC.MAINNET_PORT else self.log.info)(f"{addr}")

            try:
                result = self.rpc.addnode(addr, "onetry")

                if result is not None:
                    self.log.info(f"result: {result}")

            except HydraRPC.Exception as err:
                self.log.warn(f"addnode failed for {addr}: response={err.response} result={err.error}")

        self.log.info(f"server now reports {self.rpc.getconnectioncount()} connections")


@Test.register()
class PeerScanTest(Test):

    def test_0_peerscan_runnable(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(PeerScan, "-h")

    def test_1_peerscan_run(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(PeerScan, "-c 1")


if __name__ == "__main__":
    PeerScan.main()
