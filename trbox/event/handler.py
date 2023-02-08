from __future__ import annotations

from abc import ABC, abstractmethod
from queue import Queue
from typing import TYPE_CHECKING, TypeVar

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln
from trbox.event import Event
from trbox.event.system import Exit

if TYPE_CHECKING:
    from trbox.broker import Broker
    from trbox.console import Console
    from trbox.market import Market
    from trbox.strategy import Strategy
    from trbox.trader import Trader


class EventHandler(ABC):
    '''
    The base class for event handling ability
    '''

    def __init__(self) -> None:
        self._inbox: Queue[Event] = Queue()

    # event queue operations
    def put(self, e: Event) -> None:
        self._inbox.put(e)

    # main loop
    def run(self) -> None:
        # when a thread is start, a infinite loop will keep run
        while True:
            # block by the get method until a event is retrieved
            e = self._inbox.get()
            # Log.debug(Memo('receiving', event=cln(e)).by(self))

            # pass the event to the subclass method for handling
            self.handle(e)
            Log.debug(Memo('handled', event=cln(e)).by(self))

            # mark the task done and update event count
            self._inbox.task_done()

            # break handler if received the Exit event
            if isinstance(e, Exit):
                break

    # event handling implementation left to child
    @ abstractmethod
    def handle(self, e: Event) -> None:
        pass


Self = TypeVar('Self', bound='CounterParty')


class CounterParty(EventHandler, ABC):
    '''
    Middle class that is attached to a Trader
    '''

    def __init__(self) -> None:
        super().__init__()

    # CounterParty must attach to a Trader to function properly
    def attach(self: Self, *,
               trader: Trader,
               strategy: Strategy,
               market: Market,
               broker: Broker,
               console: Console | None) -> Self:
        self._trader = trader
        self._strategy = strategy
        self._market = market
        self._broker = broker
        self._console = console
        return self

    @property
    def trader(self) -> Trader:
        return self._trader

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @property
    def market(self) -> Market:
        return self._market

    @property
    def broker(self) -> Broker:
        return self._broker

    @property
    def console(self) -> Console | None:
        return self._console
