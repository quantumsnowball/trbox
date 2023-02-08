from abc import ABC

from typing_extensions import override

from trbox.common.types import Symbol
from trbox.event import Event
from trbox.event.handler import CounterParty


class Portfolio(CounterParty, ABC):
    def __init__(self) -> None:
        super().__init__()

    # account status

    @property
    def cash(self) -> float:
        return self._broker.cash

    @property
    def positions(self) -> dict[Symbol, float]:
        return self._broker.positions

    @property
    def equity(self) -> float:
        return self._broker.equity


class DefaultPortfolio(Portfolio):
    @override
    def handle(self, e: Event) -> None:
        pass
