from dataclasses import dataclass

from pandas import Timestamp

from trbox.common.types import Positions
from trbox.event import PortfolioEvent
from trbox.event.broker import OrderResult


@dataclass
class EquityCurveUpdate(PortfolioEvent):
    timestamp: Timestamp
    equity: float
    positions: Positions


@dataclass
class OrderResultUpdate(PortfolioEvent):
    order_result: OrderResult
