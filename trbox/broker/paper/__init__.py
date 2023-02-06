from collections import defaultdict

from typing_extensions import override

from trbox.broker import Broker
from trbox.broker.paper.engine import MatchingEngine, TradingBook
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol, Symbols
from trbox.event import Event, MarketEvent
from trbox.event.broker import Order
from trbox.event.market import Candlestick, OhlcvWindow

DEFAULT_INITIAL_FUND = 1e6


class PaperEX(Broker):
    def __init__(self,
                 symbols: Symbol | Symbols,
                 initial_fund: float = DEFAULT_INITIAL_FUND) -> None:
        super().__init__()
        self._cash: float = initial_fund
        self._positions: dict[str, float] = defaultdict(float)
        self._symbols = symbols
        if isinstance(self._symbols, Symbol):
            self._symbols = (self._symbols, )
        self._engine = MatchingEngine()

    # account state

    @property
    @override
    def cash(self) -> float:
        return self._cash

    @property
    @override
    def positions(self) -> dict[str, float]:
        return self._positions

    @property
    @override
    def positions_worth(self) -> float:
        # TODO deprecated simple algo trading only support single target asset
        worth = 0.0
        for s, pos in self._positions.items():
            price = self._engine.price(s)
            if not price:
                continue
            worth += price * pos
        return worth

    @property
    @override
    def equity(self) -> float:
        return self.cash + self.positions_worth

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

    def update_order_book(self, e: MarketEvent):
        symbol = e.symbol
        timestamp = None
        price = None

        if isinstance(e, Candlestick):
            timestamp = e.timestamp
            price = e.price
        elif isinstance(e, OhlcvWindow):
            timestamp = e.timestamp
            price = e.close

        if timestamp is not None and price is not None:
            if symbol in self._engine:
                self._engine[symbol].update(timestamp, price)
            else:
                self._engine[symbol] = TradingBook(symbol, timestamp, price)
            Log.debug(Memo('updated OrderBook',
                           e.symbol, price=price)
                      .by(self, e).tag('updated', 'book'))

            if not self.trader.signal.broker_ready.is_set():
                if len(self._engine) >= len(self._symbols):
                    self.trader.signal.broker_ready.set()
                    Log.info(Memo('order book ready')
                             .by(self).tag('orderbook', 'order', 'book', 'ready'))

    @override
    def handle(self, e: Event) -> None:
        super().handle(e)
        # handle MarketEvent when backtesting
        if self.trader.backtesting:
            if isinstance(e, MarketEvent):
                self.update_order_book(e)
