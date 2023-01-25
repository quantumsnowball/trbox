from abc import ABC, abstractmethod
from logging import info
from trbox.common.types import Symbol
from trbox.event import Event
from trbox.event.broker import Trade
from trbox.event.handler import CounterParty


class Broker(CounterParty, ABC):
    def handle(self, e: Event) -> None:
        if isinstance(e, Trade):
            info(f'Trade: {e.quantity} {e.symbol}')

    @abstractmethod
    def trade(self, symbol: Symbol, quantity: float) -> None:
        pass
