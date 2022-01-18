"""Contract call to method ID converter.

Will eventually also generate function calls based on params specified.
"""
from argparse import ArgumentParser
from hydra.util import sha

from hydra.app.cli import HydraApp
from hydra.test import Test


@HydraApp.register(name="call", desc=__doc__, version="1.00")
class Call(HydraApp):

    @staticmethod
    def parser(parser: ArgumentParser):
        parser.add_argument("func_sig", metavar="SIG", type=str, help="function signature.")

    def run(self):
        print(Call.method_id_from_sig(self.args.func_sig))

    @staticmethod
    def method_id_from_sig(func_sig: str) -> str:
        return sha.sha3(func_sig).hex()[:8]


@Test.register()
class CallTest(Test):

    def test_0_call_runnable(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(Call, "-h")

    def test_1_call_run(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(Call, "name()")


if __name__ == "__main__":
    Call.main()
