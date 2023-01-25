import time
from typing_extensions import override
from trbox.common.types import Symbol
from trbox.event.market import Candlestick
from threading import Thread
from trbox.market.datasource.streaming import StreamingSource


class DummyPrice(StreamingSource):
    '''
    This is a streaming price tick simulator.
    Upon start, it push event automatically to Strategy.
    '''

    def __init__(self,
                 symbol: Symbol,
                 n: int = 30,
                 delay: int = 1) -> None:
        super().__init__()
        self._symbol = symbol
        self._n = n
        self._delay = delay

    @override
    def start(self) -> None:
        def worker() -> None:
            # gen random price to simulate live market
            for i in range(self._n):
                self.trader.new_market_data(Candlestick(self._symbol, i))
                time.sleep(self._delay)
            # simulate the end of data
            self.trader.stop()
        # deamon thread will not block program from exiting
        t = Thread(target=worker, daemon=True)
        t.start()
