from typing import Self
from trbox.event import Event
from trbox.event.handler import EventHandler
from trbox.event.market import MarketDataRequest
from trbox.event.system import Start
from trbox.runner import Runner
from trbox.market.datasource import \
    DataSource, OnRequestSource, StreamingSource


class Market(EventHandler):
    def __init__(self, *,
                 source: DataSource) -> None:
        super().__init__()
        self._source = source

    def attach(self, runner: Runner) -> Self:
        # this will also attach DataSource in Market is init-ed
        self._source.attach(runner)
        return super().attach(runner)

    def handle(self, e: Event) -> None:
        # listen to system Start event
        if isinstance(e, Start) and \
                isinstance(self._source, StreamingSource):
            self._source.start()
        # listen to PriceDataRequest from Strategyy
        if isinstance(e, MarketDataRequest) and \
                isinstance(self._source, OnRequestSource):
            self._source.on_request(e)
