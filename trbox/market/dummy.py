from pandas import Timestamp
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.event.market import Candlestick
from trbox.market import MarketWorker

DEFAULT_N = 30


class DummyPrice(MarketWorker):
    '''
    This is a streaming price tick simulator.
    Upon start, it push event automatically to Strategy.
    '''

    def __init__(self,
                 symbol: Symbol,
                 n: int = DEFAULT_N) -> None:
        super().__init__()
        self._symbol = symbol
        self._n = n

    @override
    def working(self) -> None:
        # gen random price to simulate live market
        for i in range(self._n):
            hb = self.trader.strategy.heartbeats.get((
                self._symbol, Candlestick), None)
            if hb:
                intime = hb.wait(5)
                if not intime:
                    Log.error(Memo('timeout waiting for heartbeat')
                              .by(self).tag('timeout'))

            self.send.new_market_data(Candlestick(
                Timestamp.now(), self._symbol, i))

            if hb:
                hb.clear()

            if not self._alive.is_set():
                Log.info(Memo('requested to stop',
                              alive=self._alive.is_set())
                         .by(self))
                return

        self.trader.stop()
