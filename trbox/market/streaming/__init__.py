from abc import ABC, abstractmethod

from typing_extensions import override

from trbox.common.logger import debug
from trbox.common.logger.parser import Log
from trbox.common.utils import cln
from trbox.event import Event
from trbox.event.system import Exit, Start
from trbox.market import Market


class StreamingSource(Market, ABC):
    """
    This interface immplements the Market interface.

    It listens to Start event and start pushing event automatically.
    It could be a random generator running on a new thread, or in real
    trading, it could also be a websocket connection pushing new tick data.
    """

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
            debug(Log("requested", cln(e)).by(self).tag("start-streaming"))
        # listen to Exit event to also close any threaded DataSource
        if isinstance(e, Exit):
            self.stop()
            debug(Log("requested", cln(e)).by(self).tag("exit"))
