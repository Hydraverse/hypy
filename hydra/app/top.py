from argparse import ArgumentParser
from datetime import datetime, timedelta
import pytz
import time
import curses

from hydra.app import HydraApp
from hydra.test import Test


COLOR_GOOD = 2
COLOR_WARN = 8
COLOR_ERROR = 4
COLOR_ETC = 10


@HydraApp.register(name="top", desc="Show status periodically", version="0.1")
class TopApp(HydraApp):
    scr = None

    @staticmethod
    def parser(parser: ArgumentParser):
        parser.add_argument("-i", "--interval", type=float, default=10, help="polling interval.")
        parser.add_argument("-c", "--count", type=int, default=None, help="exit after (count) iterations.")
        parser.add_argument("-z", "--timezone", type=str, default="America/Los_Angeles", help="time zone.")
        parser.add_argument("-C", "--curses", action="store_true", help="use curses display.")
        parser.add_argument("-x", "--extended", action="store_true", help="show extended info.")

    def setup(self):
        super().setup()

        if self.args.curses:
            self._curses_setup()

    # noinspection PyShadowingBuiltins
    def display(self, print=print):
        print(datetime.now(tz=pytz.timezone(self.args.timezone)))
        print(datetime.utcnow())
        print(self.rpc.getconnectioncount())
        print(self.rpc.getestimatedannualroi())
        print()

        stakinginfo = self.rpc.getstakinginfo()

        stakinginfo["search-interval"] = timedelta(seconds=stakinginfo["search-interval"])
        stakinginfo.expectedtime = timedelta(seconds=stakinginfo.expectedtime)
        stakinginfo.weight /= 10**8
        stakinginfo.netstakeweight /= 10**8

        self.render(stakinginfo, name="getstakinginfo", print_fn=print)
        print()

        self.render(self.rpc.getwalletinfo(), name="getwalletinfo", print_fn=print)
        print()

        if self.args.extended:
            self.render(self.rpc.getmininginfo(), name="getmininginfo", print_fn=print)
            print()

    def display_curses(self):
        self.scr.clear()
        self.display(print=self.__print_curses)
        self.scr.refresh()

    def __print_curses(self, text=""):
        text = str(text)

        if not text.endswith("\n"):
            text += "\n"

        return self.scr.addstr(text)

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
