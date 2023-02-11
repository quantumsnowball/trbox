from asyncio import Future
from typing import Any

from aiohttp import web
from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.console.services import Service

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


class NextSite(Service):
    def __init__(self,
                 *args: Any,
                 port: int = 5000,
                 **kwargs: Any):
        super().__init__(*args, port=port, **kwargs)
        self._app = web.Application(middlewares=[on_request_error, ])
        self._app.add_routes(routes)
        self._runner = web.AppRunner(self._app)

    @override
    async def main(self):
        await self._runner.setup()
        site = web.TCPSite(self._runner, port=self._port)
        await site.start()
        await Future()  # run forever
