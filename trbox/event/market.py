from dataclasses import dataclass
from trbox.common.types import Symbol, Symbols
from trbox.common.utils import verify_ohlcv
from trbox.event import MarketEvent
from pandas import DataFrame


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
class PriceData(MarketEvent):
    pass


@dataclass
class OhlcvWindow(PriceData):
    symbols: Symbols
    win: DataFrame

    def __post_init__(self) -> None:
        self.win = verify_ohlcv(self.win)
        self.last = self.win.iloc[-1]
        self.datetime = self.win.index[-1]
        self.close = self.last.loc[(slice(None), 'Close')]


@dataclass
class Candlestick(PriceData):
    symbol: Symbol
    price: float
