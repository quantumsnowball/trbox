from flask import Flask
from typing_extensions import override

from trbox.common.logger import Log
from trbox.console import Console

app = Flask('trbox-console')


class FlaskConsole(Console):
    def __init__(self,
                 port: int = 3888) -> None:
        super().__init__()
        self._port = port

    @override
    def start(self) -> None:
        app.run(port=self._port)

    @override
    def stop(self) -> None:
        Log.error('How to stop flask server in Python?')

    # routes

    @app.route("/")
    def hello():
        return "<p>Hello, trbox Flask!</p>"

    @app.route('/console')
    def console():
        return "<p>Hello, trbox Flask! You are now in console!</p>"
