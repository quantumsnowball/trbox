from dataclasses import dataclass

from pandas import Timestamp

from trbox.event import MonitorEvent


@dataclass
class ProgressUpdate(MonitorEvent):
    name: str
    current: Timestamp
    start: Timestamp
    end: Timestamp
