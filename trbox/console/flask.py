import json

from flask import Flask
from pandas import DataFrame
from typing_extensions import override

from trbox.common.logger import Log
from trbox.console import Console
from trbox.trader import Trader

app = Flask('trbox-console')

GREETING = {'message': 'hello from dashboard!'}

trader: Trader | None = None
# routes


@app.route("/")
def hello() -> dict[str, str]:
    return GREETING

# TODO
# need to support websocket streaming to a charting library
# most like will be using TradingView data format
# https://tradingview.github.io/lightweight-charts/


@app.route('/console')
def console() -> dict[str, Trader | None]:
    return {'trader': trader}


@app.route('/navs')
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


@app.route('/tradelog')
def tradelog() -> str:
    if trader:
        try:
            info = trader.dashboard.trade_reacords.to_html()
        except Exception as e:
            info = str(trader.dashboard.trade_reacords)
            Log.exception(e)
            breakpoint()
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
        app.run(port=self._port)
        # blocked here?

    @override
    def stop(self) -> None:
        Log.error('How to stop flask server in Python?')
