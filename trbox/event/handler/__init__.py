from __future__ import annotations

from abc import ABC, abstractmethod
# TODO
# this Queue object is essential to overall performance of the program
# it may not need inter process safe, but must be thread safe
from queue import Queue

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln
from trbox.event import Event
from trbox.event.system import Exit


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

            # break handler if received the Exit event
            if isinstance(e, Exit):
                break

    # event handling implementation left to child
    @ abstractmethod
    def handle(self, e: Event) -> None:
        pass
