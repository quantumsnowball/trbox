from threading import Thread

from flask import Flask, send_file, send_from_directory
from flask.wrappers import Response
from flask_sock import Sock
from pandas import DataFrame
from simple_websocket import Server
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console import Console
from trbox.event import Event
from trbox.event.portfolio import EquityCurveUpdate
from trbox.trader import Trader

app = Flask('trbox-console')
sock = Sock(app,)
# need to allow cors for a local file domain client to connect?


GREETING = {'message': 'hello from dashboard!'}

trader: Trader | None = None
# routes


FRONTEND_PREFIX = 'dashboard'
# FRONTEND_LOCAL_DIR = 'tests/lab/static/'
FRONTEND_LOCAL_DIR = '../trbox-dashboard/out/'
DEFAULT_FILENAME = 'index.html'


# main html and website files

@app.route('/')
def index() -> Response:
    return send_file(f'{FRONTEND_LOCAL_DIR}{DEFAULT_FILENAME}')


@app.route(f'/<path:filename>')
def everything_else(filename) -> Response:
    return send_from_directory(FRONTEND_LOCAL_DIR, filename)


# TODO
# need to support websocket streaming to a charting library
# most like will be using TradingView data format
# https://tradingview.github.io/lightweight-charts/

# restful api paths

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

# error


@app.errorhandler(404)
def page_not_found(e: Exception):
    # if 404 not found, deliver the index.html by default
    # e.g. client side router only paths
    Log.exception(e)
    return send_file(f'{FRONTEND_LOCAL_DIR}{DEFAULT_FILENAME}')

# websocket


# @socketio.on('connect')
# def test_connect() -> None:
#     join_room('equity-curve')
#     Log.warning(f'Someone has connected to websocket')
#
#
# @socketio.on('message')
# def handle_message(message):
#     Log.critical(f'received message: {message}')
#     # send(message, broadcast=True)
#     send(message)

@sock.route('/')
def echo(ws: Server):
    while True:
        data = ws.receive()
        ws.send(data)

# trbox event handler


class FlaskSock(Console):
    def __init__(self,
                 port: int = 5000) -> None:
        super().__init__()
        self._port = port

    @override
    def start(self) -> None:
        # inject trader instance to global
        global trader
        trader = self.trader
        Log.warning('Flask Console started, trader should have assigned!')
        # start server
        try:
            server_thread = Thread(target=app.run,
                                   kwargs=dict(
                                       host='0.0.0.0',
                                       port=self._port),
                                   daemon=True)
            server_thread.start()
            # be careful must not block after this point
        except Exception as e:
            Log.exception(e)
        # blocked here?

    @override
    def stop(self) -> None:
        Log.error('How to stop flask server in Python?')

    #
    # handle events
    #

    def handle_equity_curve_update(self, e: EquityCurveUpdate):
        # socketio.send({'timestamp': e.timestamp.timestamp(),
        #                'equity': e.equity},
        #               json=True, )
        # socketio.send('EquityCurveUpdate',
        #               to='equity-curve', include_self=True)
        Log.warning(Memo('sent EquityCurveUpdate').by(self))

    @override
    def handle(self, e: Event) -> None:
        super().handle(e)
        # be careful must not block after this point
        if isinstance(e, EquityCurveUpdate):
            self.handle_equity_curve_update(e)
