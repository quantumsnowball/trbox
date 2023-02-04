import os

import pytest
from binance.spot import Spot
from dotenv import load_dotenv

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
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
