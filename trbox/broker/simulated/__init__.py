from trbox.broker.simulated.account.engine import MatchingEngine, TradingBook
from trbox.common.logger import debug
from typing_extensions import override
from trbox.broker import Broker
from trbox.common.logger.parser import Log
from trbox.common.types import Symbol
from trbox.event import Event
from trbox.event.broker import Order
from trbox.event.market import Candlestick


class PaperEX(Broker):
    def __init__(self,
                 symbol: Symbol) -> None:
        super().__init__()
        self._engine = MatchingEngine(
            **{symbol: TradingBook(symbol)})

    def trade(self, e: Order) -> None:
        # TODO adjust Account position and cash balance
        self._engine.match(e)

    @override
    def handle(self, e: Event) -> None:
        super().handle(e)
        # handle MarketData event when backtesting
        if self.trader.backtesting:
            if isinstance(e, Candlestick):
                self._engine[e.symbol].update(e.price)
                debug(Log('updated OrderBook',
                          e.symbol, price=e.price).by(self))
