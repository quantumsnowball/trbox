import logging
import pytest


@pytest.mark.lab()
def test_restful():
    logging.info('Trying out binance-connector-python restful')


@pytest.mark.lab()
def test_websocket():
    logging.info('Trying out binance-connector-python websocket')
