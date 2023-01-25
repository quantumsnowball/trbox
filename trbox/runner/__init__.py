from __future__ import annotations
from typing import TYPE_CHECKING, Any

from trbox.event.market import MarketData
if TYPE_CHECKING:
    from trbox.strategy import Strategy
    from trbox.market import Market
    from trbox.broker import Broker
from concurrent.futures import ThreadPoolExecutor, as_completed
from trbox.event.system import Exit, Start
from logging import info, exception


class Runner:
    def __init__(self, *,
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
    def market(self) -> Market:
        return self._market

    @property
    def broker(self) -> Broker:
        return self._broker

    # event routing
    def new_market_data(self, e: MarketData) -> None:
        self._strategy.put(e)

    # system controls
    def start(self) -> None:
        for handler in self._handlers:
            handler.put(Start())

    def stop(self) -> None:
        for handler in self._handlers:
            handler.put(Exit())

    # main thread pool
    def run(self) -> None:
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(h.run) for h in self._handlers]
            # notify the event handlers start
            self.start()
            # wait for future results and catch exceptions in other threads
            try:
                for future in as_completed(futures):
                    future.result()
            # catch KeyboardInterrupt first to stop threads gracefully
            except KeyboardInterrupt:
                info('KeyboardInterrupt: requested all handlers to quit.')
                self.stop()
            # if other Exception are catched, stop all threads gracefully and
            # then raise them again in main thread to fail any test cases
            except Exception as e:
                exception(e.__class__)
                self.stop()
                raise e

        info('Runner has completed.')


class Trader(Runner):
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
