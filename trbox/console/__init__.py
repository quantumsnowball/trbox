from abc import abstractmethod

from typing_extensions import override

from trbox.event import Event
from trbox.event.handler import CounterParty
from trbox.event.system import Start


class Console(CounterParty):
    '''
    Flask server running as a CounterParty
    '''

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @override
    def handle(self, e: Event) -> None:
        if isinstance(e, Start):
            self.start()
