from asyncio import AbstractEventLoop
from threading import Thread

from aiohttp import web
from socketio.asyncio_client import asyncio
from typing_extensions import override
from websockets.server import serve

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console import Console
from trbox.event import Event
from trbox.event.portfolio import EquityCurveUpdate

FRONTEND_LOCAL_DIR = '../trbox-dashboard/out/'
DEFAULT_FILENAME = 'index.html'
ENTRY_POINT = f'{FRONTEND_LOCAL_DIR}{DEFAULT_FILENAME}'

routes = web.RouteTableDef()


#
# app entry point
#
@routes.get('/')
async def index(_):
    return web.FileResponse(ENTRY_POINT)

routes.static('/', FRONTEND_LOCAL_DIR)


#
# websocket
#
async def echo(websocket):
    async for message in websocket:
        Log.critical(message)
        await websocket.send(message)


#
# error handling
#
@web.middleware
async def on_request_error(request: web.Request, handler):
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


class AioHttpServer(Console):
    def __init__(self,
                 port_website: int = 5000,
                 port_websocket: int = 8000) -> None:
        super().__init__()
        self._port_website = port_website
        self._port_websocket = port_websocket
        self._app = web.Application(middlewares=[on_request_error, ])
        self._app.add_routes(routes)
        self._runner = web.AppRunner(self._app)
        self._websocket_event_loop: AbstractEventLoop | None = None

    def run_services(self):
        def websocket():
            async def service():
                async with serve(echo, port=self._port_websocket):
                    await asyncio.Future()  # run forever
            eloop = asyncio.new_event_loop()
            self._websocket_event_loop = eloop
            eloop.run_until_complete(service())

        def website():
            async def service():
                await self._runner.setup()
                site = web.TCPSite(self._runner, port=self._port_website)
                await site.start()
                await asyncio.Future()  # run forever
            asyncio.run(service())

        # asyncio loop run in its own thread
        for service in (website, websocket, ):
            t = Thread(target=service,
                       daemon=True)
            t.start()

        Log.info(Memo(f'Starting website on port {self._port_website}'
                      f' and websocket on port {self._port_websocket}')
                 .by(self))

    @override
    def start(self) -> None:
        self.run_services()

    @override
    def stop(self) -> None:
        Log.error('Need to stop the event loop')

    #
    # handle party events
    #

    def handle_equity_curve_update(self, e: EquityCurveUpdate):
        async def do_something():
            await asyncio.sleep(1)
            Log.critical('Yeah, I will push updated info to client')
        if self._websocket_event_loop is not None:
            asyncio.run_coroutine_threadsafe(
                do_something(), self._websocket_event_loop)
        Log.warning(Memo('sent EquityCurveUpdate').by(self))

    @override
    def handle(self, e: Event) -> None:
        super().handle(e)
        # be careful must not block after this point
        if isinstance(e, EquityCurveUpdate):
            self.handle_equity_curve_update(e)
