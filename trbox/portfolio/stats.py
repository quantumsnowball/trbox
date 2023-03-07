from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypedDict

from pandas import DataFrame

if TYPE_CHECKING:
    from trbox.portfolio import Portfolio


class TradeStatsDict(TypedDict):
    count: int


class TradeStats:
    def __init__(self, trades: DataFrame):
        self.count = len(trades)

    @property
    def dict(self) -> TradeStatsDict:
        return {
            'count': self.count
        }


class StatsDict(TypedDict):
    all: TradeStatsDict
    buys: TradeStatsDict
    sells: TradeStatsDict


class Stats:
    def __init__(self,
                 portfolio: Portfolio) -> None:
        self._portfolio = portfolio
        self._trades = portfolio.dashboard.trades
        self._buys = self._trades[self._trades.Action == 'BUY']
        self._sells = self._trades[self._trades.Action == 'SELL']

    @property
    def all(self) -> TradeStats:
        return TradeStats(self._trades)

    @property
    def buys(self) -> TradeStats:
        return TradeStats(self._buys)

    @property
    def sells(self) -> TradeStats:
        return TradeStats(self._sells)

    @property
    def dict(self) -> StatsDict:
        return {
            'all': self.all.dict,
            'buys': self.buys.dict,
            'sells': self.sells.dict,
        }
