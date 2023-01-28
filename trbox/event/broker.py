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
    fee_rate: float | None = None
    fee: float | None = field(init=False, default=None)
    gross_proceeds: float | None = field(init=False, default=None)
    net_proceeds: float | None = field(init=False, default=None)

    def __post_init__(self):
        if self.result and self.price and self.quantity and self.fee_rate:
            self.gross_proceeds = -self.quantity * self.price
            self.fee = abs(self.gross_proceeds) * self.fee_rate
            self.net_proceeds = self.gross_proceeds - self.fee
