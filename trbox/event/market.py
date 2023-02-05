from dataclasses import dataclass

from pandas import DataFrame, Timestamp

from trbox.common.types import Symbol, Symbols
from trbox.common.utils import verify_ohlcv
from trbox.event import MarketEvent


@dataclass
class OhlcvWindow(MarketEvent):
    # TODO data structure need to be fine tuned
    symbols: Symbols
    win: DataFrame

    def __post_init__(self) -> None:
        self.win = verify_ohlcv(self.win)
        self.datetime = self.win.index[-1]
        self.ohlcv = self.win.iloc[-1]
        self.close = self.ohlcv.loc[(slice(None), 'Close')]


@dataclass
class Candlestick(MarketEvent):
    # TODO data structure need to be fine tuned
    price: float


@dataclass
class Kline(MarketEvent):
    """
    raw data structure:

    {
      "e": "kline",     // Event type
      "E": 123456789,   // Event time
      "s": "BNBBTC",    // Symbol
      "k": {
        "t": 123400000, // Kline start time
        "T": 123460000, // Kline close time
        "s": "BNBBTC",  // Symbol
        "i": "1m",      // Interval
        "f": 100,       // First trade ID
        "L": 200,       // Last trade ID
        "o": "0.0010",  // Open price
        "c": "0.0020",  // Close price
        "h": "0.0025",  // High price
        "l": "0.0015",  // Low price
        "v": "1000",    // Base asset volume
        "n": 100,       // Number of trades
        "x": false,     // Is this kline closed?
        "q": "1.0000",  // Quote asset volume
        "V": "500",     // Taker buy base asset volume
        "Q": "0.500",   // Taker buy quote asset volume
        "B": "123456"   // Ignore
      }
    }
    """
    open: float
    high: float
    low: float
    close: float
    volume: float
    value_traded: float
    bar_finished: bool
