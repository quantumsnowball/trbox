from collections.abc import Callable

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln, ppf
from trbox.event import Event
from trbox.event.broker import OrderResult
from trbox.event.handler import CounterParty
from trbox.event.market import Candlestick, Kline, OhlcvWindow


class Strategy(CounterParty):
    def __init__(
        self, *,
        name: str | None = None,
        on_tick: Callable[['Strategy', Candlestick], None] | None = None,
        on_kline: Callable[['Strategy', Kline], None] | None = None,
        on_window: Callable[['Strategy', OhlcvWindow], None] | None = None
    ) -> None:
        super().__init__()
        self._name = name
        # event action hook
        self._on_tick = on_tick
        self._on_kline = on_kline
        self._on_window = on_window

    def __str__(self) -> str:
        return f'{cln(self)}(name={self.name})'

    @property
    def name(self) -> str | None:
        return self._name

    def handle(self, e: Event) -> None:
        if self.trader.backtesting:
            self.trader.signal.broker_ready.wait(5)
        # for live streaming data
        if self._on_tick:
            if isinstance(e, Candlestick):
                self._on_tick(self, e)
                # TODO also Strategy need to know the number of Tick event
                # so maybe inc a counter state var here
                self.trader.signal.heartbeat.set()
        if self._on_kline:
            if isinstance(e, Kline):
                self._on_kline(self, e)
                self.trader.signal.heartbeat.set()
        # for request and response data
        if self._on_window:
            # upon receive window data, process using hook function
            if isinstance(e, OhlcvWindow):
                self._on_window(self, e)
                # tell paper market to send next market event
                self.trader.signal.heartbeat.set()
        # on order result
        if isinstance(e, OrderResult):
            # TODO may be a on_fill callback?
            Log.info(Memo('order result', ppf(e))
                     .by(self).tag('order', 'confirmation').sparse())
