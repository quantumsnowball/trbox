from logging import debug
from typing import Self
from trbox.event import Event
from trbox.event.handler import EventHandler
from trbox.event.market import MarketDataRequest
from trbox.event.system import Start
from trbox.runner import Runner
from trbox.market.datasource import DataSource
from trbox.market.datasource.streaming import StreamingSource
from trbox.market.datasource.onrequest import OnRequestSource


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
        if isinstance(e, Start):
            if isinstance(self._source, StreamingSource):
                self._source.start()
                debug((f'`{self.__class__.__name__}` '
                       'started the `StreamingSource`.'))
        # listen to MarketDataRequest from Strategy
        if isinstance(e, MarketDataRequest):
            if isinstance(self._source, OnRequestSource):
                self._source.on_request(e)
                debug((f'`{self.__class__.__name__}` '
                       'requested the `OnRequestSource`.'))
