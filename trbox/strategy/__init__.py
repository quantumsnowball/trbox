from collections.abc import Callable
from trbox.common.logger import info
from trbox.common.logger.parser import Log
from trbox.common.utils import cln, ppf
from trbox.event import Event
from trbox.event.broker import OrderResult
from trbox.event.handler import CounterParty
from trbox.event.market import OhlcvWindow, OhlcvWindowRequest, Candlestick
from trbox.event.system import Start


class Strategy(CounterParty):
    def __init__(
        self, *,
        on_tick: Callable[['Strategy', Candlestick], None] | None = None,
        on_window: Callable[['Strategy', OhlcvWindow], None] | None = None
    ) -> None:
        super().__init__()
        # event action hook
        self._on_tick = on_tick
        self._on_window = on_window

    # operations
    def request_ohlcv_window(self) -> None:
        self.send.new_market_data_request(OhlcvWindowRequest())

    def handle(self, e: Event) -> None:
        # for live streaming data
        if self._on_tick:
            if isinstance(e, Candlestick):
                self._on_tick(self, e)
        # for request and response data
        if self._on_window:
            # need to make the first request manually
            if isinstance(e, Start):
                self.request_ohlcv_window()
            # upon receive window data, process using hook function
            if isinstance(e, OhlcvWindow):
                self._on_window(self, e)
                self.request_ohlcv_window()
        # on order result
        if isinstance(e, OrderResult):
            # TODO may be a on_fill callback?
            info(Log('order filled', ppf(e))
                 .by(self).tag('order', 'confirmation').sparse())
