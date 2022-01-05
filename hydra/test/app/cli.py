from hydra.test import Test

from hydra.app.cli import HydraCLIApp


@Test.register()
class HydraCLIAppTest(Test):

    def test_app_cli_runnable(self):
        self.assertHydraAppIsRunnable(HydraCLIApp, "-h")


if __name__ == "__main__":
    Test.main()
