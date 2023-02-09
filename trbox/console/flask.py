from flask import Flask, send_file, send_from_directory
from flask.wrappers import Response
from pandas import DataFrame
from typing_extensions import override
from werkzeug.utils import secure_filename

from trbox.common.logger import Log
from trbox.console import Console
from trbox.trader import Trader

app = Flask('trbox-console')

GREETING = {'message': 'hello from dashboard!'}

trader: Trader | None = None
# routes


FRONTEND_PREFIX = 'dashboard'
# FRONTEND_LOCAL_DIR = 'tests/lab/static/'
FRONTEND_LOCAL_DIR = '../trbox-dashboard/out/'
DEFAULT_FILENAME = 'index.html'


# @app.route(f'/{FRONTEND_PREFIX}')
# @app.route(f'/{FRONTEND_PREFIX}/')
@app.route('/')
def serve_static_index() -> Response:
    try:
        return send_file(f'{FRONTEND_LOCAL_DIR}{DEFAULT_FILENAME}')
    except Exception as e:
        Log.exception(e)
        return Response('File not found.')


# @app.route(f'/{FRONTEND_PREFIX}/<path:filename>')
@app.route(f'/<path:filename>')
def serve_static(filename) -> Response:
    try:
        # return send_from_directory('~/Dev/trbox-dashboard/out/', filename)
        # app.logger.warning(f'filename={filename}')

        return send_from_directory(FRONTEND_LOCAL_DIR, filename)

        # must use relative path to our root dir
        # return send_file('tests/lab/static/index.html')

    except Exception as e:
        Log.exception(e)
        return Response('File not found.')


# TODO
# need to support websocket streaming to a charting library
# most like will be using TradingView data format
# https://tradingview.github.io/lightweight-charts/


@app.route('/rest/console')
def console() -> str:
    return 'Console'


@app.route('/rest/navs')
def navs() -> str:
    if trader:
        try:
            info = DataFrame(trader.dashboard.navs).to_html()
        except Exception as e:
            info = str(trader.dashboard.navs)
            Log.exception(e)
        if info:
            return info
        else:
            return 'no info'
    else:
        return 'no trader'


@app.route('/rest/tradelog')
def tradelog() -> str:
    if trader:
        try:
            info = trader.dashboard.trade_reacords.to_html()
        except Exception as e:
            info = 'Trade log not yet available, please come back later.'
            Log.exception(e)
        if info:
            return info
        else:
            return 'no info'
    else:
        return 'no trader'


# trbox event handler


class FlaskConsole(Console):
    def __init__(self,
                 port: int = 3000) -> None:
        super().__init__()
        self._port = port

    @override
    def start(self) -> None:
        # inject trader instance to global
        global trader
        trader = self.trader
        Log.critical('Flask Console started, trader should have assigned!')
        # start server
        try:
            app.run(port=self._port)
        except Exception as e:
            Log.exception(e)
        # blocked here?

    @override
    def stop(self) -> None:
        Log.error('How to stop flask server in Python?')
