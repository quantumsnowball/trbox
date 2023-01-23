from abc import ABC, abstractmethod
from trbox.event import Event
from trbox.event.market import Price
from trbox.event.handler import EventHandler


class Strategy(EventHandler, ABC):
    def handle(self, e: Event):
        if isinstance(e, Price):
            self.step(e)

    @abstractmethod
    def step(self, e: Price):
        pass
