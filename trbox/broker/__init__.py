from abc import ABC, abstractmethod
from trbox.event import Event
from trbox.event.broker import Trade
from trbox.event.handler import CounterParty


class Broker(CounterParty, ABC):
    def handle(self, e: Event) -> None:
        if isinstance(e, Trade):
            self.trade(e)

    @abstractmethod
    def trade(self, e: Trade) -> None:
        pass
