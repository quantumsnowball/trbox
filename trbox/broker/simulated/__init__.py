from typing import Iterable
from collections import defaultdict
from trbox.broker.simulated.engine import MatchingEngine, TradingBook
from trbox.common.logger import debug
from typing_extensions import override
from trbox.broker import Broker
from trbox.common.logger.parser import Log
from trbox.common.types import Symbol
from trbox.event import Event
from trbox.event.broker import Order
from trbox.event.market import Candlestick, OhlcvWindow


DEFAULT_INITIAL_FUND = 1e6


class PaperEX(Broker):
    def __init__(self,
                 symbols: Symbol | Iterable[Symbol],
                 initial_fund: float = DEFAULT_INITIAL_FUND) -> None:
        super().__init__()
        self._cash: float = initial_fund
        self._positions: dict[str, float] = defaultdict(float)
        if isinstance(symbols, Symbol):
            symbols = (symbols, )
        self._engine = MatchingEngine(
            **{symbol: TradingBook(symbol) for symbol in symbols})

    # state

    @property
    @override
    def cash(self) -> float:
        return self._cash

    @property
    @override
    def positions(self) -> dict[str, float]:
        return self._positions

    @property
    def equity(self) -> float:
        # TODO
        # having cash and position and market data (from MatchingEngine)
        # here I can easily calculate the current equity value
        return 0

    # operations

    @override
    def trade(self, e: Order) -> None:
        r = self._engine.match(e)
        # on valid trading result, settlement
        self.send.new_order_result(r)
        if r.quantity and r.net_proceeds:
            # adjust cash
            self._cash += r.net_proceeds
            # adjust position
            self._positions[r.order.symbol] += r.quantity

    # handler

    @override
    def handle(self, e: Event) -> None:
        super().handle(e)
        # handle MarketData event when backtesting
        if self.trader.backtesting:
            if isinstance(e, Candlestick):
                self._engine[e.symbol].update(e.price)
                debug(Log('updated OrderBook',
                          e.symbol, price=e.price)
                      .by(self, e).tag('updated', 'book'))
            elif isinstance(e, OhlcvWindow):
                for symbol in e.symbols:
                    price = e.close[symbol]
                    self._engine[symbol].update(price)
                    debug(Log('updated OrderBook',
                              symbol=symbol, price=price)
                          .by(self, e).tag('updated', 'book'))
