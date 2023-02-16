from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.portfolio.metrics import DrawdownResult
from trbox.strategy.context import Context


def assert_valid_metrics(my: Context):
    assert isinstance(my.portfolio.metrics.total_return, float)
    assert isinstance(my.portfolio.metrics.cagr, float)
    assert isinstance(my.portfolio.metrics.mu_sigma, tuple)
    assert isinstance(my.portfolio.metrics.drawdown, DrawdownResult)
    assert isinstance(my.portfolio.metrics.calmar, float)
    Log.warning(Memo('assert_valid_metrics()').tag('metrics'))
