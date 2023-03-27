from pandas import Timedelta, to_datetime
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.event.broker import AuditRequest
from trbox.event.market import TradeTick
from trbox.market import MarketWorker

DEFAULT_SINCE = '2018-01-01'
DEFAULT_PRICE = 20000
DEFAULT_N = 30


class GeneratedHistoricalTrades(MarketWorker):
    '''
    This is a streaming price tick simulator.
    Upon start, it push event automatically to Strategy.
    '''

    def __init__(self,
                 symbol: Symbol,
                 since: str = DEFAULT_SINCE,
                 price: float = DEFAULT_PRICE,
                 n: int = DEFAULT_N) -> None:
        super().__init__()
        self._symbol = symbol
        self._since = since
        self._price = price
        self._n = n

    @override
    def working(self) -> None:
        # gen random price to simulate live market
        for i in range(self._n):
            hb = self.strategy.heartbeats.get((
                self._symbol, TradeTick), None)
            if hb:
                intime = hb.wait(5)
                hb.clear()
                if not intime:
                    Log.error(Memo('timeout waiting for heartbeat')
                              .by(self).tag('timeout'))

            e = TradeTick(timestamp=to_datetime(self._since) + Timedelta(days=i),
                          symbol=self._symbol,
                          price=self._price + i)
            self.strategy.put(e)
            self.broker.put(e)
            self.portfolio.put(e)

            # TODO other parties should decide when to audit
            self.broker.put(AuditRequest(e.timestamp))

            if not self._alive.is_set():
                Log.info(Memo('requested to stop',
                              alive=self._alive.is_set())
                         .by(self))
                return

        self.trader.stop()
