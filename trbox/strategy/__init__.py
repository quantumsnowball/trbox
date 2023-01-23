from collections.abc import Callable
from trbox.event import Event
from trbox.event.handler import EventHandler
from trbox.event.market import Price


class Strategy(EventHandler):
    def __init__(
        self, *,
        on_tick: Callable[['Strategy', Price], None] | None = None
    ) -> None:
        super().__init__()
        # event action hook
        self._on_tick = on_tick

    def handle(self, e: Event) -> None:
        # for live streaming data
        if isinstance(e, Price) and self._on_tick:
            self._on_tick(self, e)
