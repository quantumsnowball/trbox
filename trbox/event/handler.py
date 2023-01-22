from abc import ABC, abstractmethod
from queue import Queue
from trbox.event import Event, Exit
from trbox.runner import Runner
import logging


class EventHandler(ABC):
    '''
    The base class for event handling ability
    '''

    def __init__(self):
        self._event_queue = Queue()

    # EventHandler must attach to a Runner to function properly
    def attach(self, runner: Runner):
        self._runner = runner
        return self

    @property
    def runner(self):
        return self._runner

    @property
    def attached(self):
        return isinstance(self._runner, Runner)

    # event queue operations
    def put(self, e: Event):
        self._event_queue.put(e)

    # main loop
    def run(self):
        # when a thread is start, a infinite loop will keep run
        while True:
            # block by the get method until a event is retrieved
            e = self._event_queue.get()
            logging.debug(f'Event {type(e)} collected.')

            # break handler if received the Exit event
            if isinstance(e, Exit):
                break

            # pass the event to the subclass method for handling
            self.handle(e)
            logging.debug(f'Event {type(e)} sent to {type(self)}.')

            # mark the task done and update event count
            self._event_queue.task_done()
            logging.debug(f'Event {type(e)} done.')

    # event handling implementation left to child
    @abstractmethod
    def handle(self, e: Event):
        pass
