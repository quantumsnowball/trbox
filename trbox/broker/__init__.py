from abc import ABC, abstractmethod
import logging
from trbox.event import Event
from trbox.event.broker import Trade
from trbox.event.handler import EventHandler


class Broker(EventHandler, ABC):
    def handle(self, e: Event):
        if isinstance(e, Trade):
            logging.info(f'Trade: {e.quantity} {e.symbol}')

    @abstractmethod
    def trade(self, symbol: str, quantity: float):
        pass
