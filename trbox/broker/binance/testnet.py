import os
from typing import Any

from binance.spot import Spot
from dotenv import load_dotenv
from typing_extensions import override

from trbox.broker import Broker
from trbox.common.types import Positions, Symbol
from trbox.event.broker import MarketOrder

load_dotenv()
API_URL = os.getenv('API_URL_BINANCE_SPOT_TESTNET')
API_KEY = os.getenv('API_KEY_BINANCE_SPOT_TESTNET')
API_SECRET = os.getenv('API_SECRET_BINANCE_SPOT_TESTNET')


class BinanceTestnet(Broker):
    def __init__(self) -> None:
        super().__init__()
        self._client = Spot(base_url=API_URL,
                            api_key=API_KEY,
                            api_secret=API_SECRET)

    @property
    @override
    def cash(self) -> float:
        return 0

    @property
    @override
    def positions(self) -> Positions:
        return {}

    @property
    @override
    def positions_worth(self) -> float:
        return 0

    @property
    @override
    def equity(self) -> float:
        return 0

    @override
    def trade(self, e: MarketOrder) -> dict[str, Any]:
        assert e.quantity != 0
        side = 'BUY' if e.quantity > 0 else 'SELL'
        result: dict[str, Any] = self._client.new_order(
            symbol=e.symbol,
            side=side,
            type='MARKET',
            quantity=abs(e.quantity))
        return result
