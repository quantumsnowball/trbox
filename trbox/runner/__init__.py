from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from trbox.strategy import Strategy
    from trbox.market import Market
from concurrent.futures import ThreadPoolExecutor, as_completed
from trbox.event import Exit, PriceFeedRequest
import logging


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
            handlers = [self.strategy,
                        self.market]
            futures = [executor.submit(h.run) for h in handlers]
            # start the market data
            self._market.put(PriceFeedRequest('BTC'))
            # wait for future results
            # also catch KeyboardInterrupt
            try:
                for future in as_completed(futures):
                    future.result()
            except KeyboardInterrupt:
                logging.info('KeyboardInterrupt: requested handlers to quit.')
                for handler in handlers:
                    handler.put(Exit())
        logging.info('Runner has completed.')


class Backtest(Runner):
    pass
