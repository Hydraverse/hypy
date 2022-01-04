#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import argparse

from hydra.app import HydraApp
from hydra.rpc import HydraRPC
from hydra.test import Test

import re


@HydraApp.register(name="peer-scan", desc="Connect to new nodes")
class PeerScan(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')
        HydraRPC.__parser__(parser)

    def run(self):
        self.log.info(f"rpc: {self.args}")
        rpc = HydraRPC.__from_parsed__(self.args)

        self.log.info(f"server reports {rpc.getconnectioncount()} connections")

        peers = rpc.getpeerinfo()
        addrs = []

        for peer in peers:
            match = re.match(r"\[(.+)]:(\d+)", peer.addr)

            if not match:
                match = re.match(r"(\d+\.\d+\.\d+\.\d+)(?::(\d+))?", peer.addr)

            addr = match.group(1) if match else peer.addr

            addrs.append(addr)

        self.log.info(f"loaded {len(peers)} peers")

        nodes = rpc.getnodeaddresses(10000)

        self.log.info(f"loaded {len(nodes)} nodes")

        nodes_add = [(node.address, node.port) for node in filter(lambda n: n.address not in addrs, nodes)]

        self.log.info(f"trying {len(nodes_add)} potential new peers")

        for addr, port in nodes_add:

            addr = f"{addr}:{port}" if ":" not in addr else f"[{addr}]:{port}"
            (self.log.debug if port != HydraRPC.MAINNET_PORT else self.log.info)(f"{addr}")

            try:
                result = rpc.addnode(addr, "onetry")

                if result is not None:
                    self.log.info(f"result: {result}")

            except HydraRPC.Error as err:
                self.log.warn(f"addnode failed for {addr}: response={err.response} result={err.result}")

        self.log.info(f"server now reports {rpc.getconnectioncount()} connections")


if __name__ == "__main__":
    PeerScan.main()
