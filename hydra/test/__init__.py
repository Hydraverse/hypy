import sys
import os
import unittest
import pytest
import inspect

from hydra import log


__all__ = "Test",


class Test(unittest.TestCase):
    __testing: bool = False
    __tests: list = []
    log = log

    @staticmethod
    def __new(cls):
        Test.__tests.append(cls)
        return cls

    @staticmethod
    def register():
        def hook(cls):
            return Test.__new(cls)

        return hook

    @staticmethod
    def isTesting():
        """Returns true if we are testing.
        """
        return Test.__testing

    def assertHydraAppIsRunnable(self, cls, *argv):
        try:
            Test.app(cls, *argv)
        except SystemExit as exc:
            self.assertEqual(exc.code, 0, "SystemExit raised with code != 0")
        except BaseException as exc:
            self.assertIsInstance(exc, SystemExit, f"type of exc is {type(exc)} instead of {SystemExit}")
        else:
            if '-h' in argv:
                self.assertFalse("didn't raise SystemExit after showing help")

            self.log.debug("warning: application did not raise SystemExit")

    @staticmethod
    def app(cls, *argv):
        sys.argv = [cls.info.name] + list(argv)
        return cls.main()

    @staticmethod
    def main(argv=None):
        """Run tests.

        Use -k <pattern> or <pattern> ... to specify test names.
        """
        if argv is None:
            argv = ()

        argv = tuple(argv)

        Test.__testing = True

        files = []

        if (not len(sys.argv[1:])) or sys.argv[1] == '-k':
            if not len(Test.__tests):
                # noinspection PyUnresolvedReferences
                import hydra.test.tests

            for cls in Test.__tests:
                fil = inspect.getfile(cls)
                files.append(fil)

        level = os.environ.get("HYPY_LOG", "DEBUG")

        args = f"-v --log-cli-level={level} --capture=sys -p no:cacheprovider --pyargs " \
               f"{' '.join(tuple(files) + argv)}".strip().split() + " ".join(sys.argv[1:]).strip().split()

        pytest.main(args)

