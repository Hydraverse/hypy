from typing import Callable, Any

from requests import Response

from hydra.rpc.base import BaseRPC


class ExplorerRPC(BaseRPC):
    URL_TEST: str = "https://testexplorer.hydrachain.org/api"
    URL_MAIN: str = "https://explorer.hydrachain.org/api"

    def __init__(self, mainnet: bool = True, *, response_factory=None):
        super().__init__(
            ExplorerRPC.URL_MAIN if mainnet else ExplorerRPC.URL_TEST,
            response_factory=(
                response_factory
                if response_factory is not None else
                BaseRPC.RESPONSE_FACTORY_JSON
            )
        )

    @property
    def mainnet(self) -> bool:
        return self.url == ExplorerRPC.URL_MAIN

    def human_link(self, typ: str, param: Any):
        return self.url.replace("/api", f"/{typ}/{param}")

    def call(self, name: str, *args, response_factory: Callable[[Response], Any] = None):
        return ExplorerRPC.__CALLS__[name](
            self,
            *args,
            response_factory=response_factory
        )

    def get_address(self, hydra_address: str, **kwds):
        return self.get(f"address/{hydra_address}", **kwds)

    def get_tx(self, txid: str, **kwds):
        return self.get(f"tx/{txid}", **kwds)

    def get_block(self, hash_or_height: [str, int], **kwds):
        return self.get(f"block/{hash_or_height}", **kwds)

    def get_contract(self, hex_address: str, **kwds):
        return self.get(f"contract/{hex_address}", **kwds)

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