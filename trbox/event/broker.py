from dataclasses import dataclass, field
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
    price: float | None = None
    quantity: float | None = None
    net_proceeds: float | None = field(init=False, default=None)

    def __post_init__(self):
        if self.price and self.quantity:
            self.net_proceeds = -self.quantity * self.price
