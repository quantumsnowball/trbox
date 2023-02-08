from abc import ABC

from typing_extensions import override

from trbox.event import Event
from trbox.event.handler import CounterParty


class Portfolio(CounterParty, ABC):
    def __init__(self) -> None:
        super().__init__()


class DefaultPortfolio(Portfolio):
    @override
    def handle(self, e: Event) -> None:
        pass
