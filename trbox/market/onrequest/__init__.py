from abc import ABC, abstractmethod

from typing_extensions import override

from trbox.common.logger import debug
from trbox.common.logger.parser import Log
from trbox.common.utils import cln
from trbox.event import Event
from trbox.event.market import MarketDataRequest
from trbox.market import Market


class OnRequestSource(Market, ABC):
    """
    This interface immplements the Market interface.

    It listens to price request from Strategy and give a single
    response each time. Usually it could be a local generator yielding
    dataframes, or in real trading, it could be a REST API endpoints sending
    price data per request.
    """

    @abstractmethod
    def on_request(self, e: MarketDataRequest) -> None:
        pass

    @override
    def handle(self, e: Event) -> None:
        # listen to MarketDataRequest from Strategy
        if isinstance(e, MarketDataRequest):
            self.on_request(e)
            debug(Log("requested", cln(e)).by(self).tag("market-data-request"))
