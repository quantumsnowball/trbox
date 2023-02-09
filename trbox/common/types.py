from pandas import DataFrame

Symbol = str
Symbols = tuple[Symbol, ...]

Positions = dict[Symbol, float]

Window = dict[Symbol, DataFrame]
