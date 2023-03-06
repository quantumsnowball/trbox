from dataclasses import dataclass

from pandas import Timestamp

from trbox.event import MonitorEvent


@dataclass
class TimelineRegistration(MonitorEvent):
    name: str
    start: Timestamp
    end: Timestamp


@dataclass
class ProgressUpdate(MonitorEvent):
    name: str
    current: Timestamp
