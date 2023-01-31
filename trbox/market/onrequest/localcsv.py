from typing_extensions import override
from pandas import Timestamp, to_datetime
from trbox.common.types import Symbol
from trbox.common.utils import trim_ohlcv_by_range_length
from trbox.event.market import \
    MarketDataRequest, OhlcvWindow, OhlcvWindowRequest
from trbox.market.onrequest import OnRequestSource
from trbox.market.utils import import_yahoo_csv, concat_dfs_by_columns


class YahooOHLCV(OnRequestSource):
    '''
    This is a relative low speed price simulator.
    It simulates market data fetch using http request/response.
    '''

    def __init__(self, *,
                 source: dict[Symbol, str],
                 start: Timestamp | str | None = None,
                 end: Timestamp | str | None = None,
                 length: int) -> None:
        super().__init__()
        self._source = source
        self._symbols = tuple(self._source.keys())
        self._start = to_datetime(start)
        self._end = to_datetime(end)
        self._length = length
        # data preprocessing
        dfs = {s: import_yahoo_csv(p) for s, p in self._source.items()}
        self._df = concat_dfs_by_columns(dfs)
        # data validation
        self._df = trim_ohlcv_by_range_length(
            self._df, self._start, self._end, self._length)
        # data ready
        self._window_generator = (win
                                  for win in self._df.rolling(self._length)
                                  if len(win) >= self._length)

    @override
    def on_request(self, e: MarketDataRequest) -> None:
        # actively listening to request
        if isinstance(e, OhlcvWindowRequest):
            try:
                df = next(self._window_generator)
                self.send.new_market_data(OhlcvWindow(self._symbols, df))
            except StopIteration:
                self.trader.stop()
