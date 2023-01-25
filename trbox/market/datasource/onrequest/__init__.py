from abc import ABC, abstractmethod
from trbox.market.datasource import DataSource
from trbox.event.market import MarketDataRequest


class OnRequestSource(DataSource, ABC):
    '''
    This object listens to price request from Strategy and give a single
    response each time. Usually it could be a local generator yielding
    dataframes, or in real trading, it could be a REST API endpoints sending
    price data per request.
    '''
    @abstractmethod
    def on_request(self, e: MarketDataRequest) -> None:
        pass
