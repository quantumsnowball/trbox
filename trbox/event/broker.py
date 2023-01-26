from dataclasses import dataclass
from trbox.common.types import Symbol
from trbox.event import BrokerEvent


@dataclass
class Trade(BrokerEvent):
    symbol: Symbol
    quantity: float


@dataclass
class Order(BrokerEvent):
    symbol: Symbol
    quantity: float


@dataclass
class MarketOrder(Order):
    pass


@dataclass
class LimitOrder(Order):
    price: float


@dataclass
class OrderResult(BrokerEvent):
    order: Order
    result: bool
