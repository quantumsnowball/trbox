import os
from pathlib import Path

from aiohttp import web
from binance.websocket.binance_socket_manager import json

from trbox.backtest.lab.constants import PY_SUFFIX, RUNDIR_PREFIX
from trbox.backtest.utils import Node


def scan_for_source(parent: Node,
                    *,
                    suffix: str = PY_SUFFIX,
                    prefix_excluded: str = RUNDIR_PREFIX,
                    basepath: str) -> Node:
    for m in os.scandir(basepath + parent.path):
        if m.is_dir() and not m.name.startswith(prefix_excluded):
            parent.add(scan_for_source(Node(m.name, 'folder', parent, []),
                                       basepath=basepath))
        elif m.is_file() and m.name.endswith(suffix):
            parent.add(Node(m.name, 'file', parent, []))
    return parent


def scan_for_result(parent: Node,
                    *,
                    prefix: str = RUNDIR_PREFIX,
                    basepath: str) -> Node:
    # loop through every items in path
    for m in os.scandir(basepath + parent.path):
        if m.is_dir():
            if m.name.startswith(prefix):
                # prefixed dir should contain run info
                db_path = f'{basepath}/{parent.path}/{m.name}/db.sqlite'
                if (Path(db_path).is_file()):
                    # meta.json should exist in a valid result dir
                    parent.add(scan_for_result(Node(m.name, 'folder', parent, []),
                                               basepath=basepath))
            else:
                # nested one level if is a dir, key is the dirname
                parent.add(scan_for_result(Node(m.name, 'folder', parent, []),
                                           basepath=basepath))
    return parent


def routes_factory(basepath: str) -> web.RouteTableDef:
    routes = web.RouteTableDef()

    async def ls_source(_: web.Request) -> web.Response:
        node = scan_for_source(Node('', 'folder', None, []),
                               basepath=basepath)
        return web.json_response(node.dict,
                                 dumps=lambda s: str(json.dumps(s, indent=4)))
    routes.get('/api/tree/source')(ls_source)

    async def ls_result(_: web.Request) -> web.Response:
        node = scan_for_result(Node('', 'folder', None, []),
                               basepath=basepath)
        return web.json_response(node.dict,
                                 dumps=lambda s: str(json.dumps(s, indent=4)))
    routes.get('/api/tree/result')(ls_result)

    return routes
