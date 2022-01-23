from hydra.rpc.base import BaseRPC


class ExplorerRPC(BaseRPC):
    URL_TEST: str = "https://testexplorer.hydrachain.org/api"
    URL_MAIN: str = "https://explorer.hydrachain.org/api"

    def __init__(self, mainnet: bool = True, *, response_factory=None):
        super().__init__(
            ExplorerRPC.URL_MAIN if mainnet else ExplorerRPC.URL_TEST,
            response_factory=response_factory
        )

    @property
    def mainnet(self) -> bool:
        return self.url == ExplorerRPC.URL_MAIN

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