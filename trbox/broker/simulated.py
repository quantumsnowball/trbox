from trbox.broker import Broker
from trbox.common.types import Symbol
from trbox.event.broker import Trade


class PaperEX(Broker):
    def trade(self,
              symbol: Symbol,
              quantity: float) -> None:
        self.put(Trade(symbol, quantity))
