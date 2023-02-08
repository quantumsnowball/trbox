from pandas import Timestamp
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.event.broker import AuditRequest
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
            hb = self.strategy.heartbeats.get((
                self._symbol, Candlestick), None)
            if hb:
                intime = hb.wait(5)
                if not intime:
                    Log.error(Memo('timeout waiting for heartbeat')
                              .by(self).tag('timeout'))

            e = Candlestick(Timestamp.now(), self._symbol, i)
            self.strategy.put(e)
            # if backtesting, broker also receive MarketEvent to simulate quote
            if self.trader.backtesting:
                self.trader.broker.put(e)
            # TODO other parties should decide when to audit
            self.trader.broker.put(AuditRequest(e.timestamp))

            if hb:
                hb.clear()

            if not self._alive.is_set():
                Log.info(Memo('requested to stop',
                              alive=self._alive.is_set())
                         .by(self))
                return

        self.trader.stop()
