from threading import Thread

from flask import Flask, send_file, send_from_directory
from flask.wrappers import Response
from flask_socketio import SocketIO, emit, join_room, send
from pandas import DataFrame
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console import Console
from trbox.event import Event
from trbox.event.portfolio import EquityCurveUpdate
from trbox.trader import Trader

app = Flask('trbox-console')
socketio = SocketIO(
    app,
    cors_allowed_origins='*',
    # async_mode='threading'
)
# need to allow cors for a local file domain client to connect
app.logger.setLevel('INFO')


GREETING = {'message': 'hello from dashboard!'}

trader: Trader | None = None
# routes


FRONTEND_PREFIX = 'dashboard'
# FRONTEND_LOCAL_DIR = 'tests/lab/static/'
FRONTEND_LOCAL_DIR = '../trbox-dashboard/out/'
DEFAULT_FILENAME = 'index.html'


@app.route('/')
def serve_static_index() -> Response:
    try:
        return send_file(f'{FRONTEND_LOCAL_DIR}{DEFAULT_FILENAME}')
    except Exception as e:
        Log.exception(e)
        return Response('File not found.')


@app.route(f'/<path:filename>')
def serve_static(filename) -> Response:
    try:
        return send_from_directory(FRONTEND_LOCAL_DIR, filename)
    except Exception as e:
        Log.exception(e)
        # TODO client cannot directly access the client side path, e.g. /tradelog
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

# websocket


@socketio.on('connect')
def test_connect() -> None:
    join_room('equity-curve')
    Log.warning(f'Someone has connected to websocket')


@socketio.on('message')
def handle_message(message):
    Log.critical(f'received message: {message}')
    # send(message, broadcast=True)
    send(message)

# trbox event handler


class FlaskSocketIO(Console):
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
            # socketio.run(app, port=self._port)
            server_thread = Thread(target=socketio.run,
                                   args=(app, ),
                                   kwargs=dict(
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
