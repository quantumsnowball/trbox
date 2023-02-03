from threading import Event, Thread

from pandas import Timestamp
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol
from trbox.event.market import Candlestick
from trbox.market import Market

DEFAULT_N = 30


class DummyPrice(Market):
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
        self._alive = Event()

    @override
    def start(self) -> None:
        def worker() -> None:
            # gen random price to simulate live market
            for i in range(self._n):
                heartbeat = self.trader.signal.heartbeat.wait(5)
                if not heartbeat:
                    Log.error(Memo('timeout waiting for heartbeat')
                              .by(self).tag('timeout'))

                self.send.new_market_data(Candlestick(
                    Timestamp.now(), self._symbol, i))

                self.trader.signal.heartbeat.clear()

                if not self._alive.is_set():
                    Log.info(Memo('requested to stop',
                                  alive=self._alive.is_set())
                             .by(self))
                    return

            self.trader.stop()

        self._alive.set()
        t = Thread(target=worker)
        t.start()

    @override
    def stop(self) -> None:
        self._alive.clear()
