import os
from collections import namedtuple
from dataclasses import dataclass
from typing import NamedTuple

import pytest
from binance.spot import Spot
from dotenv import load_dotenv

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.types import Symbol, Symbols
from trbox.common.utils import ppf

# ref:
#   testnet: https://testnet.binance.vision/
#   connector: https://binance-connector.readthedocs.io/


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
def test_exchange_info(client: Spot):
    ex_info = client.exchange_info()
    rate_limit = ex_info['rateLimits']
    Log.info(Memo(ppf(ex_info)).sparse())
    Log.info(Memo(ppf(rate_limit)).sparse())


@pytest.mark.lab()
def test_account_balance(client: Spot):
    Log.info(Memo(ppf(client.account())).sparse())


@pytest.mark.lab()
def test_account_worth(client: Spot):
    CURRENCY = 'USDT'

    acc = client.account()
    bal = {r['asset']: float(r['free']) + float(r['locked'])
           for r in acc['balances']}

    def get_position_worth(symbol: str,
                           position: float,
                           currency: str = CURRENCY) -> NamedTuple:
        Worth = namedtuple('Worth', 'position, price, worth')
        try:
            pair = f'{symbol}{currency}'
            price = float(client.ticker_price(pair)['price'])
            worth = price * position
            return Worth(position, price, worth)
        except Exception as e:
            if symbol in ['BUSD', 'USDC', 'USDT']:
                return Worth(position, 1, position)
            return Worth(position, None, None)
    worths = {sym: get_position_worth(sym, pos)
              for sym, pos in bal.items()}
    total = sum([w[2] for w in worths.values() if w])
    Log.info(Memo('Positions worth', ppf(worths)).sparse())
    Log.info(Memo(total_worth=total))


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


@pytest.mark.lab()
def test_limit_order(client: Spot):
    SYMBOL1 = 'BTC'
    SYMBOL2 = 'USDT'
    SYMBOLS = (SYMBOL1, SYMBOL2)
    SYMBOL = f'{SYMBOL1}{SYMBOL2}'
    SIDE = 'BUY'
    TYPE = 'LIMIT'
    PRICE = 23000
    QUANTITY = 0.01
    TIME_IN_FORCE = 'GTC'

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
                              price=PRICE,
                              quantity=QUANTITY,
                              timeInForce=TIME_IN_FORCE)
    Log.info(Memo(result=ppf(result)).sparse())

    # after
    Log.info(Memo('After:', ppf(get_balance(SYMBOLS))).sparse())

    # TODO
    # Problem of placing orders restfully is that you don't get notified when the
    # order is filled. You have to actively check the order status.


@pytest.mark.lab()
def test_current_open_order(client: Spot):
    SYMBOL1 = 'BTC'
    SYMBOL2 = 'USDT'
    SYMBOL = f'{SYMBOL1}{SYMBOL2}'

    orders = client.get_open_orders(symbol=SYMBOL)
    Log.info(Memo('Current open orders:', ppf(orders)).sparse())


@pytest.mark.lab()
def test_cancel_all_open_order(client: Spot):
    SYMBOL1 = 'BTC'
    SYMBOL2 = 'USDT'
    SYMBOL = f'{SYMBOL1}{SYMBOL2}'

    orders = client.cancel_open_orders(symbol=SYMBOL)
    Log.info(Memo('Cancel orders:', ppf(orders)).sparse())
