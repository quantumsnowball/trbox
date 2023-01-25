import logging
import pytest
from dotenv import load_dotenv
import os
from pprint import pformat as pp
from binance.spot import Spot
from binance.websocket.spot.websocket_client \
    import SpotWebsocketClient

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
    '''
    Yes this is totally working
    Receiving websocket live quote every second tick
    '''
    SYMBOL = 'bnbusdt'

    def message_handler(msg):
        logging.info(pp(msg))

    ws = SpotWebsocketClient()
    ws.start()
    try:
        ws.mini_ticker(symbol=SYMBOL,
                       id=1,
                       callback=message_handler)
        ws.join()
    except KeyboardInterrupt:
        ws.stop()
    except Exception as e:
        logging.exception(e)
    finally:
        ws.close()
