import logging
from trbox.event import Event
from trbox.event.broker import Trade
from trbox.event.handler import EventHandler


class Broker(EventHandler):
    def handle(self, e: Event):
        if isinstance(e, Trade):
            logging.info(f'Trade: {e.quantity} {e.symbol}')

    def trade(self,
              symbol: str,
              quantity: float):
        self.put(Trade(symbol, quantity))
