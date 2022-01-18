from hydra.rpc.base import BaseRPC


class ExplorerRPC(BaseRPC):
    TEST_URL: str = "https://testexplorer.hydrachain.org/api"
    MAIN_URL: str = "https://explorer.hydrachain.org/api"

    def __init__(self, mainnet: bool = True):
        super().__init__(
            ExplorerRPC.MAIN_URL if mainnet else ExplorerRPC.TEST_URL
        )

    def call(self, name: str, *args):
        return ExplorerRPC.__CALLS__[name](self, *args)

    def get_address(self, hydra_address: str):
        return self.get(f"address/{hydra_address}")

    def get_tx(self, txid: str):
        return self.get(f"tx/{txid}")

    def get_block(self, hash_or_height: [str, int]):
        return self.get(f"block/{hash_or_height}")

    def get_contract(self, hex_address: str):
        return self.get(f"contract/{hex_address}")

    __CALLS__ = {
        c.__name__.replace("get_", "", 1): c
        for c in
        [
            get_address,
            get_tx,
            get_block,
            get_contract
        ]
    }