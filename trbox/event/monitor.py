from dataclasses import dataclass
from typing import Any, Callable

from pandas import Timestamp

from trbox.event import MonitorEvent


@dataclass
class ProgressUpdate(MonitorEvent):
    name: str
    current: Timestamp
    start: Timestamp
    end: Timestamp


@dataclass
class EnableOutput(MonitorEvent):
    display: Callable[..., None]
    step: int
    count: int
