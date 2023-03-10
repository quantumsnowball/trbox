import asyncio
from asyncio import Future
from threading import Thread
from typing import Any

import click
from aiohttp import web
from aiohttp.typedefs import Handler
from typing_extensions import override

import trbox.backtest.lab.endpoints as endpoints
from trbox.backtest.lab.constants import ENTRY_POINT
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo


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
        self._app = web.Application(middlewares=[self.on_request_error, ])
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
    # error handling
    #

    @ web.middleware
    async def on_request_error(self,
                               request: web.Request,
                               handler: Handler) -> web.StreamResponse:
        try:
            return await handler(request)
        except web.HTTPNotFound as e404:
            # FileNotFoundError
            Log.critical(Memo(e404).by('Middleware'))
            return web.FileResponse(ENTRY_POINT)
        except Exception as e:
            # any other errors
            Log.exception(e)
            return web.FileResponse(ENTRY_POINT)

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
