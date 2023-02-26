from typing import Literal, TypedDict

from pandas import DataFrame

Symbol = str
Symbols = tuple[Symbol, ...]

Positions = dict[Symbol, float]

Window = dict[Symbol, DataFrame]


class WebSocketMessage(TypedDict):
    type: Literal['stdout', 'stderr', 'system']
    text: str
