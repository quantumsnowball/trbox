
from aiohttp import web

from trbox.backtest.lab.constants import ENTRY_POINT, FRONTEND_LOCAL_DIR

routes = web.RouteTableDef()


@routes.get('/')
async def index(_: web.Request) -> web.FileResponse:
    return web.FileResponse(ENTRY_POINT)

routes.static('/', FRONTEND_LOCAL_DIR)
