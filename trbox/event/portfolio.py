from dataclasses import dataclass

from pandas import Timestamp

from trbox.common.types import Positions
from trbox.event import PortfolioEvent


@dataclass
class EquityCurveUpdate(PortfolioEvent):
    timestamp: Timestamp
    equity: float
    positions: Positions
