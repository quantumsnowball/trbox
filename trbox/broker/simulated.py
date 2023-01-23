from trbox.broker import Broker
from trbox.event.broker import Trade


class PaperEX(Broker):
    def trade(self,
              symbol: str,
              quantity: float) -> None:
        self.put(Trade(symbol, quantity))
