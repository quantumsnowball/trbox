from pathlib import Path

from aiohttp import web

FRONTEND_LOCAL_DIR = Path(Path(__file__).parent,
                          '../../../frontend/trbox-lab/out/')
DEFAULT_FILENAME = 'index.html'
ENTRY_POINT = Path(FRONTEND_LOCAL_DIR, DEFAULT_FILENAME)


routes = web.RouteTableDef()


@routes.get('/')
async def index(_: web.Request) -> web.FileResponse:
    return web.FileResponse(ENTRY_POINT)

routes.static('/', FRONTEND_LOCAL_DIR)
