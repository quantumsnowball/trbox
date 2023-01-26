from abc import ABC, abstractmethod
from trbox.event import Event
from trbox.event.broker import Order
from trbox.event.handler import CounterParty


class Broker(CounterParty, ABC):
    def handle(self, e: Event) -> None:
        if isinstance(e, Order):
            self.trade(e)

    @abstractmethod
    def trade(self, e: Order) -> None:
        pass
