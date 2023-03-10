from collections import defaultdict
from typing import Any, Self

from pandas import MultiIndex, Series, Timestamp, concat


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
                    key: str) -> Series:
        return Series(self._marks[key], name='value')

    def __setitem__(self,
                    key: str,
                    value: Any) -> None:
        self(key, value)

    def __len__(self) -> int:
        return len(self._marks)

    @property
    def series(self) -> Series:
        names = ['name', 'timestamp']
        if len(self._marks) == 0:
            return Series([],
                          index=MultiIndex.from_tuples([], names=names),
                          name='value',
                          dtype=float)
        return concat([self[k] for k in self._marks],
                      keys=self._marks.keys(),
                      names=names)
