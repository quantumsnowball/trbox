import logging
import pytest
from dotenv import load_dotenv
import os
from binance.spot import Spot


load_dotenv()
API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')


@pytest.mark.lab()
def test_restful():
    '''
    Yes this is working
    Got client time, account balance, and klines successfully
    '''
    SYMBOL = 'BTCUSDT'

    def print_time():
        client = Spot()
        logging.info(client.time())
    print_time()

    def print_account_info():
        client = Spot(api_key=API_KEY, api_secret=API_SECRET)
        logging.info(client.account())
    # print_account_info()

    def print_kline():
        client = Spot()
        # response = client.new_order(**params)
        # logging.info(response)
        klines = client.klines(SYMBOL, '1d')
        logging.info(klines)
        breakpoint()
    print_kline()


@pytest.mark.lab()
def test_websocket():
    logging.info('Trying out binance-connector-python websocket')
