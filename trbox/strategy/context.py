from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from trbox.event import MarketEvent
from trbox.strategy.types import MemoryCell, MemorySized, Memroy
from trbox.trader import Trader

if TYPE_CHECKING:
    from trbox.broker import Broker
    from trbox.portfolio import Portfolio
    from trbox.strategy import Strategy


class Count:
    def __init__(self) -> None:
        self._i: dict[int, int] = defaultdict(lambda: 0)
        self._initial = True

    @property
    def beginning(self) -> bool:
        return self._initial

    def tick(self) -> None:
        if self._initial:
            self._initial = False
        for n, i in self._i.items():
            if i >= n:
                self._i[n] = 1
            else:
                self._i[n] += 1

    def every(self,
              n: int, *,
              initial: bool = False) -> bool:
        if self._i[n] >= n:
            return True
        if initial:
            return self._initial
        return False


@dataclass
class Context:
    strategy: Strategy
    count: Count
    event: MarketEvent | None = None
    memory: Memroy = field(init=False, kw_only=True)

    def __post_init__(self) -> None:
        class dequedict(MemorySized):
            def __missing__(self, key: int) -> MemoryCell:
                self.__setitem__(key, deque(maxlen=key))
                return self.__getitem__(key)
        self.memory = defaultdict(dequedict)

    @property
    def trader(self) -> Trader:
        return self.strategy.trader

    @property
    def broker(self) -> Broker:
        return self.strategy.broker

    @property
    def portfolio(self) -> Portfolio:
        return self.strategy.portfolio
