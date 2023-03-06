from pandas import Timedelta, Timestamp
from typing_extensions import override

from trbox.event import Event
from trbox.event.handler import CounterParty


class Monitor(CounterParty):
    def __init__(self) -> None:
        super().__init__()
        self._basis: dict[str, Timedelta] = {}
        self._progress: dict[str, Timedelta] = {}

    def handle_register(self,
                        name: str,
                        start: Timestamp,
                        end: Timestamp,) -> None:
        pass

    def handle_progress(self,
                        name: str,
                        current: Timestamp) -> None:
        # check if all strategy has registered
        # calculate overall progress
        # check if overall progress is crossing a mark
        # then print to stdout
        pass

    @ override
    def handle(self, e: Event) -> None:
        pass


monitor = Monitor()
