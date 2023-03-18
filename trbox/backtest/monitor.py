from collections import deque
from multiprocessing import Queue
from queue import Full

from pandas import Timestamp

from trbox.common.utils import localnow_string
from trbox.event import Event
from trbox.event.monitor import EnableOutput, ProgressUpdate
from trbox.event.system import Exit


class Monitor:
    def __init__(self, maxsize: int = 25) -> None:
        self._inbox: Queue[Event] = Queue(maxsize=maxsize)
        self._enable = False
        self._count = 1
        self._pcts: dict[str, float] = {}
        self._rolling: deque[float] = deque([0, 0], maxlen=2)
        self._step = 5

    # basic
    def put(self, e: Event) -> None:
        try:
            self._inbox.put_nowait(e)
        except Full:
            pass

    def run(self) -> None:
        while True:
            e = self._inbox.get()
            self.handle(e)
            # break handler if received the Exit event
            if isinstance(e, Exit):
                break

    @property
    def progress(self) -> float:
        return sum(self._pcts.values()) / self._count

    # handle events

    def handle_progress_update(self, e: ProgressUpdate) -> None:
        # update overall progress
        self._pcts[e.name] = e.pct
        # only when display is enabled
        if self._enable:
            # calculate the latest overall progress
            self._rolling.append(self.progress)
            # check if overall progress is crossing a mark
            prev, val = self._rolling
            if int(prev*100//self._step) != int(val*100//self._step) or val == 0.0 or val == 1.0:
                print(f'{localnow_string()} : {self.progress:7.2%}', flush=True)

    def handle(self, e: Event) -> None:
        if isinstance(e, ProgressUpdate):
            self.handle_progress_update(e)
        elif isinstance(e, EnableOutput):
            self._enable = True
            self._count = e.count
            self._step = e.step


# singleton instance for all traders to share
monitor = Monitor()


#
# helper
#
class Tracker:
    def __init__(self,
                 start: Timestamp,
                 end: Timestamp,
                 step: int = 5) -> None:
        self._start = start
        self._end = end
        self._step = step
        self._rolling: deque[float] = deque([0, 0], maxlen=2)
        self.total = self._end - self._start

    def update(self,
               name: str,
               current: Timestamp,) -> None:
        # calc current progress
        done = current - self._start
        pct = max(0, min(1, done / self.total))
        self._rolling.append(pct)
        # check if overall progress is crossing a mark
        prev, val = self._rolling
        if int(prev*100//self._step) != int(val*100//self._step):
            monitor.put(ProgressUpdate(name, pct))
