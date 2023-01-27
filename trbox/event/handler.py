from abc import ABC, abstractmethod
from queue import Queue
from typing import Self
from trbox.common.logger.parser import Log
from trbox.common.utils import cln
from trbox.event import Event
from trbox.event.distributor import Distributor
from trbox.event.system import Exit
from trbox.trader import Trader
from trbox.common.logger import debug


class EventHandler(ABC):
    '''
    The base class for event handling ability
    '''

    def __init__(self) -> None:
        self._event_queue: Queue[Event] = Queue()

    # event queue operations
    def put(self, e: Event) -> None:
        self._event_queue.put(e)

    # main loop
    def run(self) -> None:
        # when a thread is start, a infinite loop will keep run
        while True:
            # block by the get method until a event is retrieved
            e = self._event_queue.get()
            debug(Log('receiving', event=cln(e)).by(self))

            # pass the event to the subclass method for handling
            self.handle(e)
            debug(Log('handling', event=cln(e)).by(self))

            # mark the task done and update event count
            self._event_queue.task_done()

            # break handler if received the Exit event
            if isinstance(e, Exit):
                break

    # event handling implementation left to child
    @ abstractmethod
    def handle(self, e: Event) -> None:
        pass


class CounterParty(EventHandler, ABC):
    '''
    Middle class that is attached to a Trader
    '''

    def __init__(self) -> None:
        super().__init__()

    # CounterParty must attach to a Trader to function properly
    def attach(self,
               trader: Trader) -> Self:
        self._trader = trader
        return self

    @ property
    def trader(self) -> Trader:
        return self._trader

    @ property
    def send(self) -> Distributor:
        return self._trader._distributor

    @ property
    def attached(self) -> bool:
        return isinstance(self._trader, Trader)
