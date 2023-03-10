from trbox.backtest.lab.endpoints.operation import routes as operation
from trbox.backtest.lab.endpoints.result import routes as result
from trbox.backtest.lab.endpoints.source import routes as source
from trbox.backtest.lab.endpoints.static import routes as static
from trbox.backtest.lab.endpoints.tree import routes_factory as tree

__all__ = [
    'tree',
    'operation',
    'result',
    'source',
    'static',
]
