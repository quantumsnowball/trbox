from dataclasses import dataclass

from pandas import DataFrame, Series, Timestamp
from websockets.server import WebSocketServerProtocol

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
    client: WebSocketServerProtocol
    series: Series


@dataclass
class EquityCurveHistoryRequest(PortfolioEvent):
    client: WebSocketServerProtocol
    n: int | None


@dataclass
class OrderResultUpdate(PortfolioEvent):
    order_result: OrderResult


@dataclass
class TradeLogHistoryUpdate(PortfolioEvent):
    client: WebSocketServerProtocol
    df: DataFrame


@dataclass
class TradeLogHistoryRequest(PortfolioEvent):
    client: WebSocketServerProtocol
    n: int | None
