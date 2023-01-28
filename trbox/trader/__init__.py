from __future__ import annotations
from typing import TYPE_CHECKING, Any
from trbox.common.logger.parser import Log
from trbox.common.utils import cln
from trbox.event.broker import MarketOrder
if TYPE_CHECKING:
    from trbox.strategy import Strategy
    from trbox.market import Market
    from trbox.broker import Broker
from concurrent.futures import ThreadPoolExecutor, as_completed
from trbox.event.system import Exit, Start
from trbox.common.types import Symbol
from trbox.event.distributor import Distributor
from trbox.common.logger import info, exception


class Runner:
    def __init__(self, *,
                 strategy: Strategy,
                 market: Market,
                 broker: Broker):
        self._strategy: Strategy = strategy
        self._market: Market = market
        self._broker: Broker = broker
        self._handlers = [self._strategy, self._market, self._broker]

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
            except KeyboardInterrupt as e:
                self.stop()
                info(Log(cln(e), 'requested all handlers to quit')
                     .by(self).tag('interrupt', 'ctrl-c'))
            # if other Exception are catched, stop all threads gracefully and
            # then raise them again in main thread to fail any test cases
            except Exception as e:
                exception(e.__class__)
                self.stop()
                raise e

        info(Log('Runner has completed').by(self))


class Trader(Runner):
    def __init__(self, *,
                 live: bool = False,
                 **kwargs: Any):
        super().__init__(**kwargs)
        self._live = live
        self._distributor = Distributor(self,
                                        strategy=self._strategy,
                                        market=self._market,
                                        broker=self._broker)
        for handler in self._handlers:
            handler.attach(self)
        for handler in self._handlers:
            assert handler.attached

    # mode
    @property
    def live(self) -> bool:
        return self._live

    @property
    def backtesting(self) -> bool:
        return not self._live

    # account info
    @property
    def cash(self) -> float:
        return self._broker.account.cash

    @property
    def positions(self) -> dict[Symbol, float]:
        return self._broker.account.positions

    # investment decision
    def trade(self, symbol: Symbol, quantity: float) -> None:
        return self._broker.trade(MarketOrder(symbol, quantity))
