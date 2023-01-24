from abc import ABC, abstractmethod
from queue import Queue
from typing import Self
from trbox.event import Event
from trbox.event.system import Exit
from trbox.runner import Runner
import logging


class EventHandler(ABC):
    '''
    The base class for event handling ability
    '''

    def __init__(self) -> None:
        self._event_queue: Queue[Event] = Queue()

    # EventHandler must attach to a Runner to function properly
    def attach(self, runner: Runner) -> Self:
        self._runner = runner
        return self

    @property
    def runner(self) -> Runner:
        return self._runner

    @property
    def attached(self) -> bool:
        return isinstance(self._runner, Runner)

    # event queue operations
    def put(self, e: Event) -> None:
        self._event_queue.put(e)

    # main loop
    def run(self) -> None:
        # when a thread is start, a infinite loop will keep run
        while True:
            # block by the get method until a event is retrieved
            e = self._event_queue.get()
            logging.debug((f'`{self.__class__.__name__}` received a '
                           f'`{e.__class__.__name__}` event.'))

            # break handler if received the Exit event
            if isinstance(e, Exit):
                break

            # pass the event to the subclass method for handling
            self.handle(e)
            logging.debug((f'`{self.__class__.__name__}` is handling '
                           f'`{e.__class__.__name__}` event.'))

            # mark the task done and update event count
            self._event_queue.task_done()

    # event handling implementation left to child
    @abstractmethod
    def handle(self, e: Event) -> None:
        pass
