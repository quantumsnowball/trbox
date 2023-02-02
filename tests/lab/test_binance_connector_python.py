import os
from pprint import pformat as pp

import pytest
from binance.spot import Spot
from binance.websocket.spot.websocket_client import SpotWebsocketClient
from dotenv import load_dotenv

from trbox.common.logger import info, warning
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln

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
        info(client.time())
    print_time()

    def print_account_info():
        client = Spot(api_key=API_KEY, api_secret=API_SECRET)
        info(client.account())
    print_account_info()

    def print_kline():
        client = Spot()
        # response = client.new_order(**params)
        # info(response)
        klines = client.klines(SYMBOL, '1d')
        info(klines)
    print_kline()


@pytest.mark.lab()
def test_websocket():
    '''
    Yes this is totally working
    Receiving websocket live quote every second tick
    '''
    SYMBOL = 'btcusdt'

    def print_streaming_ticks(fn: str):
        def message_handler(msg_dict):
            info('\n' + pp(msg_dict))

        ws = SpotWebsocketClient()
        ws.start()
        try:
            match fn:
                case 'mini_ticker':
                    ws.mini_ticker(1, message_handler, symbol=SYMBOL)
                case 'trade':
                    ws.trade(SYMBOL, 2, message_handler)
                case 'kline':
                    ws.kline(SYMBOL, 3, '1m', message_handler)
                case _:
                    pass
            ws.join()
        except KeyboardInterrupt as e:
            warning(Memo(cln(e), 'user stopped execution')
                    .tag('interrupt', 'ctrl-c'))
        except Exception as e:
            raise e
        finally:
            ws.stop()
            ws.close()
    print_streaming_ticks('kline')
