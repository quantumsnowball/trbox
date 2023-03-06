from pandas import Timedelta, Timestamp
from typing_extensions import override

from trbox.event import Event
from trbox.event.handler import CounterParty
from trbox.event.monitor import ProgressUpdate, TimelineRegistration


class Monitor(CounterParty):
    def __init__(self) -> None:
        super().__init__()
        self._basis: dict[str, Timedelta] = {}
        self._progress: dict[str, Timedelta] = {}

    def handle_timeline_register(self, e: TimelineRegistration) -> None:
        self._basis[e.name] = e.end - e.start

    def handle_progress_update(self, e: ProgressUpdate) -> None:
        # check if all strategy has registered
        # calculate overall progress
        # check if overall progress is crossing a mark
        # then print to stdout
        print(e)

    @ override
    def handle(self, e: Event) -> None:
        if isinstance(e, ProgressUpdate):
            self.handle_progress_update(e)
        elif isinstance(e, TimelineRegistration):
            self.handle_timeline_register(e)


monitor = Monitor()
