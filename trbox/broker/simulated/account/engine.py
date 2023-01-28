from dataclasses import dataclass
from trbox.common.logger import info
from trbox.common.logger.parser import Log
from trbox.common.types import Symbol
from trbox.common.utils import ppf
from trbox.event.broker import LimitOrder, MarketOrder, Order, OrderResult


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
        info(Log('order matching', ppf(e_result)).sparse()
             .by(self).tag('match', 'order'))
        return e_result
