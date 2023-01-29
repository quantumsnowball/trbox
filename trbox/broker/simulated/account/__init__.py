from collections import defaultdict
from typing_extensions import override


class PaperAccount:
    def __init__(self,
                 initial_fund: float) -> None:
        self._cash: float = initial_fund
        self._positions: dict[str, float] = defaultdict(float)

    # cash
    @property
    @override
    def cash(self) -> float:
        return self._cash

    @cash.setter
    def cash(self, cash: float) -> None:
        self._cash = cash

    # positions
    @property
    @override
    def positions(self) -> dict[str, float]:
        return self._positions
