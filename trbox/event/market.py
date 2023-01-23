from dataclasses import dataclass
from trbox.common.types import Symbol
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
class OhlcvWindow(MarketEvent):
    symbol: Symbol
    df: DataFrame


@dataclass
class Price(MarketEvent):
    price: float
