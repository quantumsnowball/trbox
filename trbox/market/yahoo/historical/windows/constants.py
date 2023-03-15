from pathlib import Path
from typing import Literal

CACHE_DIR = f'{Path.home()}/.local/share/trbox'

ERROR = 5  # days

ABSOLUTE_START = 0  # timestamp for yahoo url period1

Freq = Literal['1d',]
