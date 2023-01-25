from binance.spot import Spot
from typing_extensions import override
from trbox.event import Event
from trbox.market.datasource.onrequest import OnRequestSource


class BinanceRestful(OnRequestSource):
    def __init__(self, api_key: str, api_secret: str) -> None:
        super().__init__()
        self._client = Spot(api_key=api_key,
                            api_secret=api_secret)

    def on_server_time(self) -> None:
        pass

    @override
    def on_request(self, e: Event) -> None:
        pass
