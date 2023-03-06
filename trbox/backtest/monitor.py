from typing_extensions import override

from trbox.event import Event
from trbox.event.handler import CounterParty
from trbox.event.monitor import ProgressUpdate


class Monitor(CounterParty):
    def __init__(self) -> None:
        super().__init__()
        self._progress: dict[str, float] = {}

    @property
    def progress(self):
        return sum(self._progress.values()) / len(self._progress)

    # handle events

    def handle_progress_update(self, e: ProgressUpdate) -> None:
        # check if all strategy has registered
        # calculate overall progress
        total = e.end - e.start
        done = e.current - e.start
        progress = done / total
        self._progress[e.name] = max(0, min(1, progress))
        # check if overall progress is crossing a mark
        # then print to stdout
        print(f'{self.progress:.2%}')

    @ override
    def handle(self, e: Event) -> None:
        if isinstance(e, ProgressUpdate):
            self.handle_progress_update(e)


# singleton instance for all traders to share
monitor = Monitor()
