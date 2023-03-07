from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from pandas import DataFrame, Timestamp

if TYPE_CHECKING:
    from trbox.portfolio import Portfolio


class TradeStatsDict(TypedDict):
    count: int
    avg_interval: float | None
    avg_quantity: float | None


class TradeStats:
    def __init__(self, trades: DataFrame):
        self._trades = trades
        self._start: Timestamp | None = trades.index[0] if self.count > 0 else None
        self._end: Timestamp | None = trades.index[-1] if self.count > 0 else None

    @property
    def count(self) -> int:
        return len(self._trades)

    @property
    def avg_interval(self) -> float | None:
        if self.count >= 2 and self._start and self._end:
            delta = self._end - self._start
            return delta.days / (self.count - 1)
        return None

    @property
    def avg_quantity(self) -> float | None:
        if self.count > 0:
            return self._trades['Quantity'].mean()
        return None

    @property
    def dict(self) -> TradeStatsDict:
        return {
            'count': self.count,
            'avg_interval': self.avg_interval,
            'avg_quantity': self.avg_quantity,
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
