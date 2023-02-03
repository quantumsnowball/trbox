from dataclasses import dataclass

from pandas import DataFrame, Timestamp

from trbox.common.types import Symbol, Symbols
from trbox.common.utils import verify_ohlcv
from trbox.event import MarketEvent


@dataclass
class OhlcvWindow(MarketEvent):
    symbols: Symbols
    win: DataFrame

    def __post_init__(self) -> None:
        self.win = verify_ohlcv(self.win)
        self.datetime = self.win.index[-1]
        self.ohlcv = self.win.iloc[-1]
        self.close = self.ohlcv.loc[(slice(None), 'Close')]


@dataclass
class Candlestick(MarketEvent):
    symbol: Symbol
    price: float
