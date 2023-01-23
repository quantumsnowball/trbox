from dataclasses import dataclass
from trbox.event import Event


class BrokerEvent(Event):
    pass


@dataclass
class Trade(BrokerEvent):
    symbol: str
    quantity: float
