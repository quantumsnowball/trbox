from __future__ import annotations
from typing import TYPE_CHECKING

from trbox.event import PriceFeedRequest
if TYPE_CHECKING:
    from trbox.strategy import Strategy
    from trbox.market import Market
from concurrent.futures import ThreadPoolExecutor


class Runner:
    def __init__(self,
                 strategy: Strategy,
                 market: Market):
        self._strategy = strategy.attach(self)
        self._market = market.attach(self)
        for handler in [self._strategy, self._market]:
            assert handler.attached

    # refs to major event handlers
    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @property
    def market(self) -> Market:
        return self._market

    # main thread pool
    def run(self):
        with ThreadPoolExecutor() as executor:
            executor.submit(self._strategy.run)
            executor.submit(self._market.run)
            # start the market data
            self._market.put(PriceFeedRequest('BTC'))


class Backtest(Runner):
    pass
