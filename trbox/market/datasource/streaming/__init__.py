from abc import ABC, abstractmethod
from trbox.market.datasource import DataSource


class StreamingSource(DataSource, ABC):
    '''
    This object listens to Start event and start pushing event automatically.
    It could be a random generator running on a new thread, or in real
    trading, it could also be a websocket connection pushing new tick data.
    '''
    @abstractmethod
    def start(self) -> None:
        pass
