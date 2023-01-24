from trbox.event import Event
from trbox.event.market import OhlcvWindow, OhlcvWindowRequest
from trbox.market import Market
from trbox.market.utils import import_yahoo_csv


class YahooOHLCV(Market):
    '''
    This is a relative low speed price simulator
    simulating market data fetch using http request/response
    '''

    def __init__(self,
                 file_path: str,
                 length: int) -> None:
        super().__init__()
        self._file_path = file_path
        self._length = length
        # data preprocessing here
        self._df = import_yahoo_csv(self._file_path)
        self._window_generator = (win
                                  for win in self._df.rolling(self._length)
                                  if len(win) >= self._length)

    def handle(self, e: Event) -> None:
        # actively listening to request
        if isinstance(e, OhlcvWindowRequest):
            try:
                next_df = next(self._window_generator)
                self.runner.strategy.put(OhlcvWindow('BTC', next_df))
            except StopIteration:
                self.runner.stop()
