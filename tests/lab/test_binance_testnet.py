import os

import pytest
from binance.spot import Spot
from dotenv import load_dotenv

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol, Symbols
from trbox.common.utils import ppf

# ref: https://testnet.binance.vision/


load_dotenv()
API_URL = os.getenv('API_URL_BINANCE_SPOT_TESTNET')
API_KEY = os.getenv('API_KEY_BINANCE_SPOT_TESTNET')
API_SECRET = os.getenv('API_SECRET_BINANCE_SPOT_TESTNET')


@pytest.fixture(scope='module')
def client() -> Spot:
    return Spot(base_url=API_URL,
                api_key=API_KEY,
                api_secret=API_SECRET)


@pytest.mark.lab()
def test_account_balance(client: Spot):
    Log.info(client.time())
    Log.info(Memo(ppf(client.account())).sparse())


@pytest.mark.lab()
def test_market_order(client: Spot):
    SYMBOL1 = 'BTC'
    SYMBOL2 = 'USDT'
    SYMBOLS = (SYMBOL1, SYMBOL2)
    SYMBOL = f'{SYMBOL1}{SYMBOL2}'
    SIDE = 'BUY'
    TYPE = 'MARKET'
    QUANTITY = 0.01

    def get_balance(symbols: Symbols) -> tuple[dict[str, str]]:
        bal = client.account()['balances']
        pos = tuple(x for x in bal if x['asset'] in symbols)
        return pos

    # before
    Log.info(Memo('Before:', ppf(get_balance(SYMBOLS))).sparse())

    # trade
    result = client.new_order(symbol=SYMBOL,
                              side=SIDE,
                              type=TYPE,
                              quantity=QUANTITY)
    Log.info(Memo(result=ppf(result)).sparse())

    # after
    Log.info(Memo('After:', ppf(get_balance(SYMBOLS))).sparse())
