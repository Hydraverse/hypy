from hydra.test import Test

from hydra.app.rpc import HydraRPCApp


@Test.register()
class HydraRPCAppTest(Test):

    def test_app_rpc_runnable(self):
        self.assertHydraAppIsRunnable(HydraRPCApp, "-h")


if __name__ == "__main__":
    Test.main()
