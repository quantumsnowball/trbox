from dataclasses import dataclass

from trbox.event import MonitorEvent


@dataclass
class ProgressUpdate(MonitorEvent):
    name: str
    pct: float


@dataclass
class EnableOutput(MonitorEvent):
    step: int
    count: int
