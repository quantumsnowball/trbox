from __future__ import annotations

from dataclasses import dataclass
from threading import Event
from typing import TYPE_CHECKING, Any

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln
from trbox.event.broker import MarketOrder
from trbox.trader.dashboard import Dashboard

if TYPE_CHECKING:
    from trbox.strategy import Strategy
    from trbox.market import Market
    from trbox.broker import Broker
    from trbox.console import Console

from concurrent.futures import ThreadPoolExecutor, as_completed

from trbox.common.types import Symbol
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
        self._handlers = [self._strategy, self._market, self._broker]
        if console:
            self._console: Console = console
            self._handlers.append(self._console)
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
                Log.info(Memo(cln(e), 'requested all handlers to quit')
                         .by(self).tag('interrupt', 'ctrl-c'))
            # if other Exception are catched, stop all threads gracefully and
            # then raise them again in main thread to fail any test cases
            except Exception as e:
                Log.exception(e.__class__)
                self.stop()
                raise e

        Log.info(Memo('Runner has completed').by(self))
        # TODO but what about live trading? how to get some report without
        # terminating the Trader?


class Trader(Runner):
    def __init__(self, *,
                 live: bool = False,
                 **kwargs: Any):
        super().__init__(**kwargs)
        self._live = live
        for handler in self._handlers:
            handler.attach(self)
        for handler in self._handlers:
            assert handler.attached
        # TODO How do you control when to log the equity value? should I pass
        # in a user arg and determine from it?
        self._dashboard = Dashboard()

    # mode

    @property
    def live(self) -> bool:
        return self._live

    @property
    def backtesting(self) -> bool:
        return not self._live

    # other parties

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @property
    def broker(self) -> Broker:
        return self._broker

    @property
    def market(self) -> Market:
        return self._market

    # account status

    @property
    def cash(self) -> float:
        return self._broker.cash

    @property
    def positions(self) -> dict[Symbol, float]:
        return self._broker.positions

    @property
    def equity(self) -> float:
        return self._broker.equity

    # dashboard
    @property
    def dashboard(self) -> Dashboard:
        return self._dashboard
        # TODO I think user should be able to request the dashboard as long as
        # the Trader is still running. It should contain the lastest trading
        # result regardless live trading or backtesting.

    # account operations

    def trade(self, symbol: Symbol, quantity: float) -> None:
        return self._broker.trade(MarketOrder(symbol, quantity))

    # helpers

    # TODO
    # these helpers should confirm there is no pending order first
    # otherwise may issue multiple order causing wrong rebalance ratio

    def rebalance(self,
                  symbol: Symbol,
                  pct_target: float,
                  ref_price: float,
                  pct_min: float = 0.01) -> None:
        target_value = self.equity * pct_target
        net_value = target_value - self._broker.positions_worth
        if abs(net_value / self.equity) < pct_min:
            return
        target_quantity = net_value / ref_price
        Log.info(Memo(target_quantity=target_quantity)
                 .by(self).sparse())
        self._broker.trade(MarketOrder(symbol, target_quantity))

    def clear(self, symbol: Symbol) -> None:
        raise NotImplementedError
