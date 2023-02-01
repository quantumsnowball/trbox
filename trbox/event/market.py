from dataclasses import dataclass

from pandas import DataFrame

from trbox.common.types import Symbol, Symbols
from trbox.common.utils import verify_ohlcv
from trbox.event import MarketEvent

#
# Requests
#


@dataclass
class MarketDataRequest(MarketEvent):
    pass


@dataclass
class OhlcvWindowRequest(MarketDataRequest):
    pass


#
# Response
#


@dataclass
class MarketData(MarketEvent):
    pass


@dataclass
class OhlcvWindow(MarketData):
    symbols: Symbols
    win: DataFrame

    def __post_init__(self) -> None:
        self.win = verify_ohlcv(self.win)
        self.datetime = self.win.index[-1]
        self.ohlcv = self.win.iloc[-1]
        self.close = self.ohlcv.loc[(slice(None), "Close")]


@dataclass
class Candlestick(MarketData):
    symbol: Symbol
    price: float
