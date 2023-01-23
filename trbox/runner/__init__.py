from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from trbox.strategy import Strategy
    from trbox.market import Market
    from trbox.broker import Broker
from concurrent.futures import ThreadPoolExecutor, as_completed
from trbox.event.system import Exit
from trbox.event.market import PriceFeedRequest
import logging


class Runner:
    def __init__(self,
                 strategy: Strategy,
                 market: Market,
                 broker: Broker):
        self._strategy: Strategy = strategy.attach(self)
        self._market: Market = market.attach(self)
        self._broker: Broker = broker.attach(self)
        self._handlers = [self._strategy, self._market, self._broker]
        for handler in self._handlers:
            assert handler.attached

    # refs to major event handlers
    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @property
    def market(self) -> Market:
        return self._market

    @property
    def broker(self) -> Broker:
        return self._broker

    # system controls
    def stop(self) -> None:
        for handler in self._handlers:
            handler.put(Exit())

    # main thread pool
    def run(self) -> None:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(h.run) for h in self._handlers]
            # start the market data
            self._market.put(PriceFeedRequest('BTC'))
            # wait for future results
            # also catch KeyboardInterrupt
            try:
                for future in as_completed(futures):
                    future.result()
            except KeyboardInterrupt:
                logging.info(
                    'KeyboardInterrupt: requested all handlers to quit.')
                self.stop()
        logging.info('Runner has completed.')


class Backtest(Runner):
    pass
