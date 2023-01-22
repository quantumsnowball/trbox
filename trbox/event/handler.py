from abc import ABC, abstractmethod
from queue import Queue
from trbox.event import Event
from trbox.runner import Runner


class EventHandler(ABC):
    '''
    The base class for event handling ability
    '''

    def __init__(self):
        self._event_queue = Queue()

    def attach(self, runner: Runner):
        self._runner = runner
        return self

    @property
    def attached(self):
        return isinstance(self._runner, Runner)

    def put(self, e: Event):
        self._event_queue.put(e)

    def run(self):
        # when a thread is start, a infinite loop will keep run
        while True:
            # block by the get method until a event is retrieved
            e = self._event_queue.get()
            # pass the event to the subclass method for handling
            self.handle(e)
            # mark the task done and update event count
            self._event_queue.task_done()

    @abstractmethod
    def handle(self, e: Event):
        pass
