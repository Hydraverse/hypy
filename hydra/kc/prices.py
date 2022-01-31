from datetime import timedelta
from typing import Optional, Tuple

from kucoin.client import Client
from currencies import Currency


__all__ = "PriceClient",

from util.tlru import TimedLRU


class PriceClient:
    coin: str
    kuku: Client

    _incln: bool
    _currc: Currency
    _cache: TimedLRU[str, Optional[str]]

    # Generated 2022-01-31
    _avail: Tuple[str] = ('AED', 'ARS', 'AUD', 'BDT', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'COP', 'CZK', 'DKK', 'DZD', 'EUR', 'GBP', 'HKD', 'HRK', 'IDR', 'ILS', 'INR', 'JPY', 'KRW', 'KWD', 'KZT', 'MXN', 'MYR', 'NGN', 'NOK', 'NZD', 'PHP', 'PKR', 'PLN', 'RON', 'RUB', 'SAR', 'SEK', 'SGD', 'THB', 'TRY', 'TWD', 'UAH', 'USD', 'VND', 'ZAR')

    def __init__(self, api_key: str, api_secret: str, passphrase: str, *, coin: str = "HYDRA", include_names: bool = False, sandbox: bool = False, request_params=None):
        self.coin = coin
        self._incln = include_names
        self.kuku = Client(api_key, api_secret, passphrase, sandbox=sandbox, requests_params=request_params)

        self._currc = Currency("USD")
        self._cache = TimedLRU(expiry=timedelta(minutes=5), cache=self.__price)

        self.__init__avail()

    def __init__avail(self):
        if len(self._avail):
            return

        _avail = []

        for currency in Currency.get_currency_formats():  # type: str
            if self._cache[currency] is not None:
                _avail.append(currency)

        self._avail = tuple(_avail)

    @property
    def currencies(self) -> tuple:
        return self._avail

    def price(self, currency: str) -> Optional[str]:
        return self._cache[currency]

    def __price(self, currc: str) -> Optional[str]:
        rslt = self.kuku.get_fiat_prices(currc, self.coin)
        value = rslt.get(self.coin, None)

        if value is not None:
            self._currc.set_money_currency(currc)
            return (
                self._currc.get_money_format(value)
                if not self._incln else
                self._currc.get_money_with_currency_format(value)
            )





