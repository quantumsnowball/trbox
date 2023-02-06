import threading
from collections import deque
from dataclasses import dataclass
from typing import Any, Protocol

from trbox.common.types import Symbol
from trbox.event import MarketEvent
from trbox.strategy.context import Context


class Hook(Protocol):
    def __call__(self, my: Context) -> None:
        ...


@dataclass
class DataHandler:
    context: Context
    hook: Hook


DataStreamId = tuple[Symbol, type[MarketEvent]]

DataHandlers = dict[DataStreamId, DataHandler]

Heartbeats = dict[DataStreamId, threading.Event]

Memroy = dict[str, dict[int, deque[Any]]]
