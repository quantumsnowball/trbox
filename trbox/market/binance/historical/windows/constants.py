from pathlib import Path
from typing import Literal

from pandas import Timedelta

CACHE_DIR = f'{Path.home()}/.local/share/trbox'

API_BASE = 'https://api.binance.com'
ARCHIVE_BASE = 'https://data.binance.vision/data'

MarketType = Literal[
    'spot',
    # 'futures', # not implemented yet
]
UpdateFreq = Literal[
    'daily',
    # 'monthly', # not implemented yet
]
DataType = Literal[
    # 'aggTrades', # not implemented yet
    'klines',
    # 'trades', # not implemented yet
]
Freq = Literal['1s',
               '1m', '3m', '5m', '15m', '30m',
               '1h', '2h', '4h', '6h', '8h', '12h',
               '1d', ]

MAX_GAP: dict[Freq, Timedelta] = {
    # default 5 units of the bar size
    '1s': Timedelta(seconds=5),
    '1m': Timedelta(minutes=5),
    '3m': Timedelta(minutes=15),
    '5m': Timedelta(minutes=25),
    '15m': Timedelta(minutes=75),
    '30m': Timedelta(minutes=150),
    '1h': Timedelta(hours=5),
    '2h': Timedelta(hours=10),
    '4h': Timedelta(hours=20),
    '6h': Timedelta(hours=30),
    '8h': Timedelta(hours=40),
    '12h': Timedelta(hours=60),
    '1d': Timedelta(days=5),
}
ERROR = 5  # days

RAW_COLUMNS = ['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime',
               'AssetVolume', 'NumberOfTrades', 'TakerBaseAssetVolume', 'TakerQuoteAssetVolume', 'Unused']
SELECTED_COLUMNS = ['Open', 'High', 'Low',
                    'Close', 'Volume', 'CloseTime']
