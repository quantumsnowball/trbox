from dataclasses import dataclass
from trbox.common.logger import debug, info
from typing_extensions import override
from trbox.broker import Broker
from trbox.common.types import Symbol
from trbox.common.utils import cln
from trbox.event import Event
from trbox.event.broker import LimitOrder, MarketOrder, Order, OrderResult
from trbox.event.market import Candlestick


@dataclass
class TradingBook:
    symbol: Symbol
    price: float | None = None
    spread: float = 0.001

    @property
    def bid(self) -> float | None:
        return self.price * (1 - self.spread / 2) if self.price else None

    @property
    def ask(self) -> float | None:
        return self.price * (1 + self.spread / 2) if self.price else None

    # update book status on related MarketData
    def update(self, price: float) -> None:
        self.price = price

        # transaction
    def transact(self, e: Order) -> OrderResult:
        def match_rules() -> tuple[bool, float | None]:
            # make sure trading book is ready
            if not (self.price and self.bid and self.ask):
                return False, None
            # assume MarketOrder always succeed
            if isinstance(e, MarketOrder):
                if e.quantity > 0:
                    return True, self.ask
                if e.quantity < 0:
                    return True, self.bid
            # assume LimitOrder is a success if price can match
            if isinstance(e, LimitOrder):
                if e.quantity > 0 and e.price > self.ask:
                    return True, self.ask
                if e.quantity < 0 and e.price < self.bid:
                    return True, self.bid
            # default Failed
            return False, None
        result, price = match_rules()
        quantity = e.quantity if result else None
        return OrderResult(e, result, price, quantity)


class MatchingEngine(dict[Symbol, TradingBook]):
    # matching
    def match(self, e: Order) -> OrderResult:
        e_result = self[e.symbol].transact(e)
        info(f'{cln(self)}: {e_result}')
        return e_result


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
                debug(
                    f'Updated OrderBook status of {e.symbol} to price={e.price}')
