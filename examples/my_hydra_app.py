#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import argparse
import json

from hydra.app import HydraApp
from hydra.test import Test


@HydraApp.register(name="myapp", desc="A Custom Hydra Tool App", version="1.0")
class MyHydraApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument("-H", "--hello", action="store_true", help="say hello")

    def run(self):
        """Do something useful.
        """
        self.log.info(f"args = {self.args}")

        if self.args.hello:
            self.log.print("Hello, World!")

        info = self.rpc.getinfo()

        self.render(result=info, name="getinfo")


@Test.register()
class MyHydraAppTest(Test):

    MY_FIRST_TEST_FIX = False

    def test_0_my_hydra_app_runnable(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(MyHydraApp, "-h")

    def test_0a_my_hydra_app_run_default(self):
        """Test running the app.
        """
        self.assertHydraAppIsRunnable(MyHydraApp)

    def test_1_my_hydra_app_validate_fix(self):
        """
        """
        self.assertTrue(MyHydraAppTest.MY_FIRST_TEST_FIX)


if __name__ == "__main__":
    MyHydraApp.main()
