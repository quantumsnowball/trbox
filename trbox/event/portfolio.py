from dataclasses import dataclass

from pandas import Series, Timestamp

from trbox.common.types import Positions
from trbox.event import PortfolioEvent
from trbox.event.broker import OrderResult


@dataclass
class EquityCurveUpdate(PortfolioEvent):
    timestamp: Timestamp
    equity: float
    positions: Positions


@dataclass
class EquityCurveHistoryUpdate(PortfolioEvent):
    series: Series


@dataclass
class EquityCurveHistoryRequest(PortfolioEvent):
    n: int | None


@dataclass
class OrderResultUpdate(PortfolioEvent):
    order_result: OrderResult
