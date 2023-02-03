from dataclasses import dataclass

from pandas import Timestamp

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.common.utils import ppf
from trbox.event.broker import LimitOrder, MarketOrder, Order, OrderResult

SPREAD = 0.001  # spread 0.1%
FEE_RATE = 0.001  # assume 0.1%
# TODO slippage


@dataclass
class TradingBook:
    symbol: Symbol
    timestamp: Timestamp | None = None
    price: float | None = None
    spread: float = SPREAD
    fee_rate: float = FEE_RATE

    @property
    def bid(self) -> float | None:
        return self.price * (1 - self.spread / 2) if self.price else None

    @property
    def ask(self) -> float | None:
        return self.price * (1 + self.spread / 2) if self.price else None

    # update book status on related MarketEvent
    def update(self, timestamp: Timestamp, price: float) -> None:
        self.timestamp = timestamp
        self.price = price

    # transaction
    def transact(self, e: Order) -> OrderResult:
        def match_rules() -> tuple[bool, float | None]:
            # make sure trading book is ready
            if not (self.price and self.bid and self.ask):
                Log.warning(Memo('trading book not ready',
                                 price=self.price, bid=self.bid, ask=self.ask)
                            .by(self).tag('trading', 'book'))
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
        return OrderResult(self.timestamp, e, result,
                           price=price, quantity=quantity, fee_rate=self.fee_rate)


class MatchingEngine(dict[Symbol, TradingBook]):
    # book state
    def price(self, symbol: Symbol) -> float | None:
        return self[symbol].price
    # matching

    def match(self, e: Order) -> OrderResult:
        e_result = self[e.symbol].transact(e)
        Log.info(Memo('matching', ppf(e)).sparse()
                 .by(self).tag('match', 'order'))
        return e_result
