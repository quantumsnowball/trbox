from threading import Thread

import aiohttp
from aiohttp import web
from socketio.asyncio_client import asyncio
from typing_extensions import override

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


@routes.get('/ws')
async def websocket_handler(request):
    Log.critical('hey ws, do you copy?')
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        # sample msg: WSMessage(type=<WSMsgType.TEXT: 1>, data='1676103725066', extra='')
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            Log.critical('ws connection closed with exception %s' %
                         ws.exception())

    Log.critical('websocket connection closed')

    return ws


routes.static('/', FRONTEND_LOCAL_DIR)

#
# websocket
#


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
                 port: int = 5000) -> None:
        super().__init__()
        self._port = port
        self._app = web.Application(middlewares=[on_request_error, ])
        self._app.add_routes(routes)
        self._runner = web.AppRunner(self._app)

    def run_server(self):
        async def run():
            await self._runner.setup()
            site = web.TCPSite(self._runner, port=self._port)
            await site.start()
            while True:
                await asyncio.sleep(3600)  # sleep forever
        # asyncio loop run in its own thread
        server_thread = Thread(target=asyncio.run, args=(run(), ), daemon=True)
        server_thread.start()

    @override
    def start(self) -> None:
        self.run_server()

    @override
    def stop(self) -> None:
        Log.error('Need to stop the event loop')

    #
    # handle party events
    #

    def handle_equity_curve_update(self, e: EquityCurveUpdate):
        Log.warning(Memo('sent EquityCurveUpdate').by(self))

    @override
    def handle(self, e: Event) -> None:
        super().handle(e)
        # be careful must not block after this point
        if isinstance(e, EquityCurveUpdate):
            self.handle_equity_curve_update(e)
