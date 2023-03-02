from collections.abc import Callable
from typing import Any

from trbox.common.types import Symbol
from trbox.event.market import OhlcvWindow
from trbox.strategy import Strategy
from trbox.strategy.context import Context
from trbox.strategy.types import Hook


def regular_rebalance(symbol: Symbol, pct_target: float) -> Hook:
    def do_rebalance(my: Context[OhlcvWindow]) -> None:
        e = my.event
        assert isinstance(e, OhlcvWindow)
        my.portfolio.rebalance(symbol, pct_target, e.close)
    return do_rebalance


class BuyAndHold(Strategy):
    def __init__(self,
                 symbol: Symbol,
                 pct_target: float = 1.0,
                 *args: Any,
                 **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.on(symbol, OhlcvWindow, do=regular_rebalance(symbol, pct_target))
