
from threading import Thread

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

routes = web.RouteTableDef()


@routes.get('/')
async def index(request: web.Request):
    Log.critical(str(request))
    return web.FileResponse(f'{FRONTEND_LOCAL_DIR}{DEFAULT_FILENAME}')

routes.static('/', FRONTEND_LOCAL_DIR)


class AioHttpServer(Console):
    def __init__(self,
                 port: int = 5000) -> None:
        super().__init__()
        self._port = port
        self._app = web.Application()
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
        server_thread = Thread(target=asyncio.run, args=(run(), ))
        server_thread.start()

    @override
    def start(self) -> None:
        # web.run_app(self._app, port=self._port)
        self.run_server()
        Log.critical('You must not block me!')

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
