from aiohttp import web
from aiohttp.typedefs import Handler

from trbox.backtest.lab.constants import ENTRY_POINT
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo


@web.middleware
async def on_request_error(request: web.Request,
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
