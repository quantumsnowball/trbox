from __future__ import annotations

from typing import TYPE_CHECKING

from pandas import DataFrame

if TYPE_CHECKING:
    from trbox.portfolio import Portfolio


class Stats:
    def __init__(self,
                 portfolio: Portfolio) -> None:
        self._portfolio = portfolio
        self._trades = portfolio.dashboard.trades

    @property
    def trades(self) -> DataFrame:
        return self._trades

    @property
    def buys(self) -> DataFrame:
        return self.trades[self.trades.Action == 'BUY']

    @property
    def sells(self) -> DataFrame:
        return self.trades[self.trades.Action == 'SELL']

    @property
    def trade_count(self) -> int:
        return len(self.trades)

    @property
    def buy_count(self) -> int:
        return len(self.buys)

    @property
    def sell_count(self) -> int:
        return len(self.sells)

    @property
    def df(self) -> DataFrame:
        return DataFrame(dict(
            trade_count=self.trade_count,
            buy_count=self.buy_count,
            sell_count=self.sell_count,
        ), index=[self._portfolio.strategy.name, ])
