#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
import argparse

from hydra.app import HydraApp
from hydra.test import Test


@HydraApp.register(name="myapp", desc="A Custom Hydra Tool App")
class MyHydraApp(HydraApp):

    @staticmethod
    def parser(parser: argparse.ArgumentParser):
        parser.add_argument('-V', '--version', action='version', version='%(prog)s 1.0')

    def run(self):
        """Do something useful.
        """
        self.log.print("Hello, World!")
        self.log.info(f"args = {self.args}")


@Test.register()
class MyHydraAppTest(Test):

    MY_FIRST_TEST_FIX = True

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
