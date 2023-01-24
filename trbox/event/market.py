from dataclasses import dataclass
from trbox.common.types import Symbol
from trbox.common.utils import verify_ohlcv
from trbox.event import MarketEvent
from pandas import DataFrame


#
# Requests
#

@dataclass
class OhlcvWindowRequest(MarketEvent):
    symbol: Symbol
    length: int


@dataclass
class PriceFeedRequest(MarketEvent):
    symbol: Symbol


#
# Response
#

@dataclass
class PriceData(MarketEvent):
    symbol: Symbol


@dataclass
class OhlcvWindow(PriceData):
    win: DataFrame

    def __post_init__(self) -> None:
        self.win = verify_ohlcv(self.win)
        self.last = self.win.iloc[-1]
        self.datetime = self.win.index[-1]
        self.close = self.win.Close[-1]


@dataclass
class Price(PriceData):
    price: float
