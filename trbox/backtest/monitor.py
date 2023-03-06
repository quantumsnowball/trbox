from collections import deque
from collections.abc import Callable

from typing_extensions import override

from trbox.event import Event
from trbox.event.handler import CounterParty
from trbox.event.monitor import EnableOutput, ProgressUpdate


class Monitor(CounterParty):
    def __init__(self) -> None:
        super().__init__()
        self._enable = False
        self._count = 1
        self._pcts: dict[str, float] = {}
        self._rolling: deque[float] = deque([0, 0], maxlen=2)
        self._step = 5

    @property
    def progress(self) -> float:
        return sum(self._pcts.values()) / self._count

    # handle events

    def handle_progress_update(self, e: ProgressUpdate) -> None:
        # calculate overall progress
        total = e.end - e.start
        done = e.current - e.start
        pct = max(0, min(1, done / total))
        self._pcts[e.name] = pct
        # only when display is enabled
        if self._enable:
            # calculate the latest overall progress
            self._rolling.append(self.progress)
            # check if overall progress is crossing a mark
            prev, val = self._rolling
            if int(prev*100//self._step) != int(val*100//self._step):
                print(f'{self.progress:.2%}', flush=True)

    @ override
    def handle(self, e: Event) -> None:
        if isinstance(e, ProgressUpdate):
            self.handle_progress_update(e)
        elif isinstance(e, EnableOutput):
            self._enable = True
            self._count = e.count
            self._step = e.step


# singleton instance for all traders to share
monitor = Monitor()
