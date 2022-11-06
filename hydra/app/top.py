from argparse import ArgumentParser
from datetime import datetime, timedelta
import pytz
import time
import curses

from attrdict import AttrDict

from hydra.app import HydraApp
from hydra.rpc.base import BaseRPC
from hydra.test import Test


COLOR_GOOD = 2
COLOR_WARN = 8
COLOR_ERROR = 4
COLOR_ETC = 10


@HydraApp.register(name="top", desc="Show status periodically", version="0.1")
class TopApp(HydraApp):
    scr = None
    ljust = None

    @staticmethod
    def parser(parser: ArgumentParser):
        parser.add_argument("-i", "--interval", type=float, default=10, help="polling interval.")
        parser.add_argument("-c", "--count", type=int, default=None, help="exit after (count) iterations.")
        parser.add_argument("-z", "--timezone", type=str, default="America/Los_Angeles", help="time zone.")
        parser.add_argument("-C", "--curses", action="store_true", help="use curses display.")
        parser.add_argument("-x", "--extended", action="store_true", help="show extended info.")

    def setup(self):
        super().setup()

        self.ljust = (30 if not self.args.full else 40)

        if self.args.curses:
            self._curses_setup()

    def run(self):
        interval = self.args.interval
        count = self.args.count
        display = self.display if not self.args.curses else self.display_curses

        try:
            while True:
                display()

                if count is not None:
                    count -= 1
                    if count <= 0:
                        break

                time.sleep(interval)

        finally:
            if self.args.curses:
                self._curses_cleanup()

    def read(self):
        result = AttrDict()

        result.now = datetime.now(tz=pytz.timezone(self.args.timezone))
        result.utcnow = datetime.utcnow()
        result.connectioncount = self.rpc.getconnectioncount()
        result.apr = self.rpc.getestimatedannualroi()

        stakinginfo = self.rpc.getstakinginfo()

        stakinginfo["search-interval"] = timedelta(seconds=stakinginfo["search-interval"])
        # noinspection PyTypeChecker
        stakinginfo.expectedtime = timedelta(seconds=stakinginfo.expectedtime)
        stakinginfo.weight /= 10**8
        stakinginfo.netstakeweight /= 10**8

        if "errors" in stakinginfo and not stakinginfo.errors:
            del stakinginfo["errors"]

        if not self.args.extended:
            TopApp.__try_delete(stakinginfo, "pooledtx")
            
        result.stakinginfo = stakinginfo

        walletinfo = self.rpc.getwalletinfo()

        if "unlocked_until" in walletinfo:
            walletinfo.unlocked_until = datetime.fromtimestamp(walletinfo.unlocked_until)

        if not self.args.extended:
            TopApp.__try_delete(walletinfo, "walletversion")
            TopApp.__try_delete(walletinfo, "keypoololdest")
            TopApp.__try_delete(walletinfo, "keypoolsize")
            TopApp.__try_delete(walletinfo, "keypoolsize_hd_internal")
            TopApp.__try_delete(walletinfo, "paytxfee")
            TopApp.__try_delete(walletinfo, "private_keys_enabled")

            if "unconfirmed_balance" in walletinfo and not walletinfo.unconfirmed_balance:
                del walletinfo.unconfirmed_balance

            if "immature_balance" in walletinfo and not walletinfo.immature_balance:
                del walletinfo.immature_balance

        TopApp.__try_delete(walletinfo, "hdseedid")

        if not len(walletinfo.walletname) and not self.args.json:
            walletinfo.walletname = "''"
            
        result.walletinfo = walletinfo

        if self.args.extended:
            mininginfo = self.rpc.getmininginfo()

            if "errors" in mininginfo and not mininginfo.errors:
                del mininginfo.errors

            if "warnings" in mininginfo and not mininginfo.warnings:
                del mininginfo.warnings

            result.mininginfo = mininginfo

        return result

    # noinspection PyShadowingBuiltins
    def display(self, print=print):
        result = self.read()

        if not self.args.json:
            for key, value in result.items():
                if not isinstance(value, AttrDict):
                    print(key.ljust(self.ljust) + str(value))
                else:
                    print()
                    self.render(value, name=key, print_fn=print, ljust=self.ljust)

        else:
            self.render(result, name="top", print_fn=print, ljust=self.ljust)

    def display_curses(self):
        self.scr.clear()
        self.display(print=self.__print_curses)
        self.scr.refresh()

    def __print_curses(self, text=""):
        text = str(text)

        if not text.endswith("\n"):
            text += "\n"

        return self.scr.addstr(text)

    @staticmethod
    def __try_delete(dic: dict, key: str):
        if key in dic:
            del dic[key]

    # noinspection PyMethodMayBeStatic
    def _curses_cleanup(self):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def _curses_setup(self):
        self.scr = curses.initscr()

        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()

        if curses.can_change_color():
            curses.init_color(curses.COLOR_BLACK, 0, 0, 0)
            curses.init_color(curses.COLOR_WHITE, 255, 255, 255)
            curses.init_color(curses.COLOR_GREEN, 0, 255, 0)
            curses.init_color(curses.COLOR_YELLOW, 255, 255, 0)
            curses.init_color(curses.COLOR_RED, 255, 0, 0)
            curses.init_color(curses.COLOR_MAGENTA, 255, 0, 255)

        curses.init_pair(1, curses.COLOR_WHITE, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(10, curses.COLOR_YELLOW, -1)



@Test.register()
class TopAppTest(Test):

    MY_FIRST_TEST_FIX = False

    def test_0_top_runnable(self):
        self.assertHydraAppIsRunnable(TopApp, "-h")


if __name__ == "__main__":
    TopApp.main()

