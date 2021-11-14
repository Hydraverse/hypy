from hydra.test import Test


@Test.register()
class HydraRPCTest(Test):

    def test_rpc_stub(self):
        self.assertTrue(True, "test stub")


if __name__ == "__main__":
    Test.main()
