from trbox.common.types import Symbol, Symbols
from trbox.event.market import \
    MarketDataRequest, OhlcvWindow, OhlcvWindowRequest
from trbox.market.datasource import OnRequestSource
from trbox.market.utils import import_yahoo_csv, concat_dfs_by_columns


class YahooOHLCV(OnRequestSource):
    '''
    This is a relative low speed price simulator.
    It simulates market data fetch using http request/response.
    '''

    def __init__(self,
                 source: dict[Symbol, str],
                 length: int) -> None:
        super().__init__()
        self._source = source
        self._symbols = tuple(self._source.keys())
        self._length = length
        # data preprocessing here
        dfs = {s: import_yahoo_csv(p) for s, p in self._source.items()}
        self._df = concat_dfs_by_columns(dfs)
        assert len(self._df) > self._length
        self._window_generator = (win
                                  for win in self._df.rolling(self._length)
                                  if len(win) >= self._length)

    def on_request(self, e: MarketDataRequest) -> None:
        # actively listening to request
        if isinstance(e, OhlcvWindowRequest):
            try:
                df = next(self._window_generator)
                self.runner.strategy.put(OhlcvWindow(self._symbols, df))
            except StopIteration:
                self.runner.stop()
