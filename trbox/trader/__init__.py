from __future__ import annotations

from dataclasses import dataclass
from threading import Event
from typing import TYPE_CHECKING, Any

from trbox.backtest.monitor import Monitor, monitor
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln
from trbox.console.dummy import DummyConsole
from trbox.portfolio import Basic, Portfolio
from trbox.portfolio.dashboard import Dashboard
from trbox.strategy.mark import Mark

if TYPE_CHECKING:
    from trbox.strategy import Strategy
    from trbox.market import Market
    from trbox.broker import Broker
    from trbox.console import Console

from concurrent.futures import ThreadPoolExecutor, as_completed

from trbox.event.system import Exit, Start


@dataclass
class Signal:
    enter: Event
    broker_ready: Event


class Runner:
    def __init__(self, *,
                 strategy: Strategy,
                 market: Market,
                 broker: Broker,
                 console: Console | None = None):
        self._strategy: Strategy = strategy
        self._market: Market = market
        self._broker: Broker = broker
        self._console: Console = console if console else DummyConsole()
        self._portfolio: Portfolio = Basic()
        # TODO now this the same instance of monitor, but using multiple threads to run it
        # it doesn't crash because the queue object is thread safe and only one thread can
        # get the progress event and print, and will receive the Exit event to shutdown itself
        # but this seems anti-pattern, should refactor the code to use a separated thread/process
        # to run the monitor.run() method
        self._monitor: Monitor = monitor
        self._handlers = (self._strategy,
                          self._market,
                          self._broker,
                          self._console,
                          self._portfolio,
                          self._monitor, )
        self._signal = Signal(enter=Event(),
                              broker_ready=Event())

    # system controls
    def start(self) -> None:
        for handler in self._handlers:
            handler.put(Start())

    def stop(self) -> None:
        for handler in self._handlers:
            handler.put(Exit())

    @property
    def signal(self) -> Signal:
        return self._signal

    # main thread pool
    def run(self) -> None:
        with ThreadPoolExecutor(thread_name_prefix='TraderPool') as executor:
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
                Log.info(Memo(cln(e), 'requested all handlers to quit')
                         .by(self).tag('interrupt', 'ctrl-c'))
            # if other Exception are catched, stop all threads gracefully and
            # then raise them again in main thread to fail any test cases
            except Exception as e:
                Log.exception(e.__class__)
                self.stop()
                raise e

        Log.info(Memo('Runner has completed').by(self))


class Trader(Runner):
    def __init__(self, *,
                 live: bool = False,
                 **kwargs: Any):
        super().__init__(**kwargs)
        self._live = live
        for handler in self._handlers:
            handler.attach(trader=self,
                           strategy=self._strategy,
                           market=self._market,
                           broker=self._broker,
                           portfolio=self._portfolio,
                           console=self._console,
                           monitor=self._monitor)

    # mode

    @property
    def live(self) -> bool:
        return self._live

    @property
    def backtesting(self) -> bool:
        return not self._live

    # portfolio
    @property
    def name(self) -> str:
        return self._strategy.name

    @property
    def portfolio(self) -> Portfolio:
        return self._portfolio

    @property
    def dashboard(self) -> Dashboard:
        return self._portfolio.dashboard

    @property
    def mark(self) -> Mark:
        return self._strategy.mark
