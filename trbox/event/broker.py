from dataclasses import dataclass
from trbox.common.types import Symbol
from trbox.event import BrokerEvent


@dataclass
class Trade(BrokerEvent):
    symbol: Symbol
    quantity: float
