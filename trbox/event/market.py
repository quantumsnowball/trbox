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


class PriceFeedRequest(MarketEvent):
    def __init__(self,
                 symbol: Symbol):
        self._symbol = symbol


#
# Response
#
class OhlcvWindow(MarketEvent):
    dfs: dict[Symbol, DataFrame]


class Price(MarketEvent):
    def __init__(self, price: float):
        self._price = price

    @property
    def price(self) -> float:
        return self._price
