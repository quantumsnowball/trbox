from pathlib import Path
from typing import Literal

CACHE_DIR = f'{Path.home()}/.local/share/trbox'

MAX_GAP = 5  # days

Freq = Literal['1d',]
