from collections.abc import Callable

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.event.market import OhlcvWindow
from trbox.strategy import Strategy


def regular_rebalance(
    symbol: Symbol,
    pct_target: float
) -> Callable[[Strategy, OhlcvWindow], None]:
    def on_window(self: Strategy, e: OhlcvWindow) -> None:
        self.trader.rebalance(symbol, pct_target, e.close[symbol])
    return on_window


class BuyAndHold(Strategy):
    def __init__(self,
                 symbol: Symbol,
                 pct_target: float = 1.0) -> None:
        super().__init__(
            on_window=regular_rebalance(symbol, pct_target))
