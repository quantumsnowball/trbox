from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar, Union

from trbox.common.types import Symbol
from trbox.event import MarketEvent
from trbox.event.market import Candlestick, Kline, OhlcvWindow

if TYPE_CHECKING:
    from trbox.strategy.context import Context


T_co = TypeVar('T_co', bound=MarketEvent, covariant=True)


class Hook(Protocol[T_co]):
    def __call__(self, my: Context[T_co]) -> None:
        ...


@dataclass
class DataHandler:
    context: Context[MarketEvent]
    hook: Hook[MarketEvent]


DataStreamId = tuple[Symbol, type[MarketEvent]]

DataHandlers = dict[DataStreamId, DataHandler]

Heartbeats = dict[DataStreamId, threading.Event]


MemoryCell = deque[Any]
MemorySized = dict[int, MemoryCell]
Memroy = dict[str, MemorySized]
