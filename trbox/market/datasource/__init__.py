from abc import ABC, abstractmethod
from typing import Self
from trbox.event.market import MarketDataRequest
from trbox.runner import Runner


class DataSource:
    '''
    DataSource is not a EventHandler, and does not have any event queue.
    It handles data for Market, and can access runner for putting events
    to other handlers.
    '''

    def attach(self, runner: Runner) -> Self:
        self._runner = runner
        return self

    @property
    def runner(self) -> Runner:
        return self._runner


class StreamingSource(DataSource, ABC):
    '''
    This object listens to Start event and start pushing event automatically.
    It could be a random generator running on a new thread, or in real 
    trading, it could also be a websocket connection pushing new tick data.
    '''
    @abstractmethod
    def start(self):
        pass


class OnRequestSource(DataSource, ABC):
    '''
    This object listens to price request from Strategy and give a single
    response each time. Usually it could be a local generator yielding 
    dataframes, or in real trading, it could be a REST API endpoints sending
    price data per request.
    '''
    @abstractmethod
    def on_request(self, e: MarketDataRequest):
        pass
