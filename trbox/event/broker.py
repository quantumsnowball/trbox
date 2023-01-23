from dataclasses import dataclass
from trbox.event import BrokerEvent


@dataclass
class Trade(BrokerEvent):
    symbol: str
    quantity: float
