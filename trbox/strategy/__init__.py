from collections.abc import Callable
from trbox.event import Event
from trbox.event.handler import EventHandler
from trbox.event.market import OhlcvWindow, OhlcvWindowRequest, Price
from trbox.event.system import Start


class Strategy(EventHandler):
    def __init__(
        self, *,
        on_tick: Callable[['Strategy', Price], None] | None = None,
        on_window: Callable[['Strategy', OhlcvWindow], None] | None = None
    ) -> None:
        super().__init__()
        # event action hook
        self._on_tick = on_tick
        self._on_window = on_window

    # operations
    def request_ohlcv_window(self) -> None:
        self.runner.market.put(OhlcvWindowRequest())

    def handle(self, e: Event) -> None:
        # for live streaming data
        if self._on_tick:
            if isinstance(e, Price):
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
