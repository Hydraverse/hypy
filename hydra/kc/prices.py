from datetime import timedelta
from typing import Optional, Tuple, Dict

from kucoin.client import Client
from currencies import Currency


__all__ = "PriceClient",

from hydra.util.tlru import TimedLRU


class PriceClient:
    coin: str
    kuku: Client

    _currc: Currency
    _cache: TimedLRU[str, Optional[str]]

    # Generated 2022-01-31
    _avail: Tuple[str] = ('AED', 'ARS', 'AUD', 'BDT', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'COP', 'CZK', 'DKK', 'DZD', 'EUR', 'GBP', 'HKD', 'HRK', 'IDR', 'ILS', 'INR', 'JPY', 'KRW', 'KWD', 'KZT', 'MXN', 'MYR', 'NGN', 'NOK', 'NZD', 'PHP', 'PKR', 'PLN', 'RON', 'RUB', 'SAR', 'SEK', 'SGD', 'THB', 'TRY', 'TWD', 'UAH', 'USD', 'VND', 'ZAR')

    _syms: Dict[str, str]

    def __init__(self, api_key: str, api_secret: str, passphrase: str, *, coin: str = "HYDRA", sandbox: bool = False, request_params=None):
        self.coin = coin
        self.kuku = Client(api_key, api_secret, passphrase, sandbox=sandbox, requests_params=request_params)

        self._currc = Currency("USD")
        self._cache = TimedLRU(expiry=timedelta(minutes=5), cache=self.__price)

        self.__init__avail()

    def __init__avail(self):
        if not len(self._avail):
            _avail = []

            for currency in Currency.get_currency_formats():  # type: str
                if self._cache[currency] is not None:
                    _avail.append(currency)

            self._avail = tuple(_avail)

        self._syms = {}

        for curr in self._avail:
            self._syms[curr] = Currency(curr).get_money_format("0").replace("0", "").strip()

    @property
    def currencies(self) -> tuple:
        return self._avail

    def symbol(self, currency: str) -> str:
        return self._syms[currency]

    def price(self, currency: str, *, raw=False, with_name=False) -> Optional[str]:
        if currency not in self.currencies:
            raise ValueError("Invalid currency.")

        value = self._cache[currency]

        return (
            value if raw else
            self.format(currency, value, with_name=with_name)
        )

    def format(self, currency: str, value, *, with_name=False):
        self._currc.set_money_currency(currency)

        return (
            self._currc.get_money_format(value) if not with_name else
            self._currc.get_money_with_currency_format(value)
        )

    def __price(self, currc: str) -> Optional[str]:
        rslt = self.kuku.get_fiat_prices(currc, self.coin)
        return rslt.get(self.coin, None)
