import shutil
from pathlib import Path

from aiohttp import web

routes = web.RouteTableDef()


@routes.delete('/api/operation/{path:.+}')
async def delete_resource(request: web.Request) -> web.Response:
    path = Path(request.match_info['path'])
    if path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)
    print(f'deleted {path}')
    return web.Response()
