from abc import ABC, abstractmethod

from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln
from trbox.event import Event
from trbox.event.handler import CounterParty
from trbox.event.system import Exit, Start


class Market(CounterParty, ABC):
    '''
    Market extens CounterParty interface.

    It listens to Start event and start pushing event automatically.
    It could be a random generator running on a new thread, or in real
    trading, it could also be a websocket connection pushing new tick data.
    '''
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @override
    def handle(self, e: Event) -> None:
        # listen to system Start event
        if isinstance(e, Start):
            self.start()
            Log.debug(Memo('requested', cln(e))
                      .by(self).tag('start-streaming'))
        # listen to Exit event to also close any threaded DataSource
        if isinstance(e, Exit):
            self.stop()
            Log.debug(Memo('requested', cln(e))
                      .by(self).tag('exit'))
