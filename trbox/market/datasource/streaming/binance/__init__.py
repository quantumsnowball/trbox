from typing_extensions import override
from trbox.market.datasource.streaming import StreamingSource


class BinanceRestful(StreamingSource):
    @override
    def start(self) -> None:
        pass
