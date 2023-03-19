from abc import ABC, abstractmethod
from threading import Thread

from binance.websocket.binance_socket_manager import threading
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln
from trbox.event import Event
from trbox.event.handler.counterparty import CounterParty
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


class MarketWorker(Market, ABC):
    def __init__(self) -> None:
        super().__init__()
        self._alive = threading.Event()

    @abstractmethod
    def working(self) -> None:
        pass

    @override
    def start(self) -> None:

        def worker() -> None:
            try:
                self.working()
            except Exception as e:
                # raise e
                # even raise will silenced the Exception if not happen in the main thread
                # P.S. only get printed out when main thread joined at the end
                # log exception can at least print out the trace stack
                Log.exception(e)

        self._alive.set()
        t = Thread(target=worker, name='MarketWorker')
        t.start()

    @override
    def stop(self) -> None:
        self._alive.clear()
