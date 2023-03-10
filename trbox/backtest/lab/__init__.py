import asyncio
from asyncio import Future
from threading import Thread
from typing import Any

import click
from aiohttp import web
from typing_extensions import override

import trbox.backtest.lab.endpoints as endpoints
from trbox.backtest.lab.endpoints.error import on_request_error


class Lab(Thread):
    def __init__(self,
                 path: str,
                 *args: Any,
                 host: str,
                 port: int,
                 **kwargs: Any) -> None:
        super().__init__(*args,
                         **kwargs)
        self.name = 'Lab'
        self._path = path
        self._host = host
        self._port = port
        # error
        self._app = web.Application(middlewares=[on_request_error, ])
        # match api first
        self._app.add_routes(endpoints.tree(self._path))
        self._app.add_routes(endpoints.source)
        self._app.add_routes(endpoints.result)
        self._app.add_routes(endpoints.operation)
        # then serve index and all other statics
        self._app.add_routes(endpoints.static)
        # app
        self._runner = web.AppRunner(self._app)

    #
    # main loop
    #

    async def serve(self) -> None:
        # aiohttp does not support CORS by default
        click.echo(f'Serving {self._path} at http://{self._host}:{self._port}')
        await self._runner.setup()
        site = web.TCPSite(self._runner, host=self._host, port=self._port)
        await site.start()
        await Future()  # run forever

    @ override
    def run(self) -> None:
        asyncio.run(self.serve())
