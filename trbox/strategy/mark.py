from collections import defaultdict
from typing import Any, Self

from pandas import Timestamp

from trbox.event import MarketEvent


class Mark:
    def __init__(self) -> None:
        self._marks: dict[str, dict[Timestamp, float]] = defaultdict(dict)
        self._timestamp: Timestamp

    def update(self,
               timestamp: Timestamp) -> Self:
        self._timestamp = timestamp
        return self

    def __call__(self,
                 key: str,
                 value: Any) -> None:
        if self._timestamp is not None:
            self._marks[key][self._timestamp] = value

    def __getitem__(self,
                    key: str) -> dict[Timestamp, float]:
        return self._marks[key]

    def __setitem__(self,
                    key: str,
                    value: Any) -> None:
        self(key, value)
