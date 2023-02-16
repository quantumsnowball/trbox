import pytest
from pandas import DataFrame, Series, Timedelta, Timestamp

from trbox.portfolio.metrics import (DrawdownPoints, DrawdownResult, cagr,
                                     detect_annualize_factor, drawdown,
                                     mu_sigma, sharpe, total_return)


def int_ls(start, n):
    return list(range(start, start+n))


def float_ls(start, n):
    return [float(i) for i in range(start, start+n)]


def str_ls(start, n):
    return [str(float(i)) for i in range(start, start+n)]


def datetime_ls(start, n):
    return [Timestamp(2015, 1, 1) + Timedelta(days=i)
            for i in range(start, start+n)]


LS_COLLECTIONS = [int_ls, float_ls, str_ls, datetime_ls]

#
# tests
#


@pytest.mark.parametrize('data_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('index_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('start', [10, 100, 1000])
@pytest.mark.parametrize('n', [10, 100, 1000])
@pytest.mark.parametrize('sample_size', [10, 50, 100, ])
def test_detect_annualize_factor(data_ls, index_ls, start, n, sample_size):
    data = data_ls(start, n)
    index = index_ls(start, n)
    series = Series(data, index=index)
    df = DataFrame({'a': data, 'b': data}, index=index)
    if index_ls in [datetime_ls, ]:
        assert detect_annualize_factor(series, sample_size)
        assert detect_annualize_factor(df, sample_size)
    else:
        with pytest.raises(Exception):
            detect_annualize_factor(series, sample_size)
        with pytest.raises(Exception):
            detect_annualize_factor(df, sample_size)


@pytest.mark.parametrize('data_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('index_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('start', [10, 100, 1000])
@pytest.mark.parametrize('n', [10, 100, 1000])
def test_total_return(data_ls, index_ls, start, n):
    data = data_ls(start, n)
    index = index_ls(start, n)
    series = Series(data, index=index)
    if data_ls in [int_ls, float_ls, ]:
        ans = total_return(series)
        assert isinstance(ans, float)
        assert ans == data[-1]/data[0]-1
    else:
        with pytest.raises(Exception):
            total_return(series)


@pytest.mark.parametrize('data_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('index_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('start', [10, 100, 1000])
@pytest.mark.parametrize('n', [10, 100, 1000])
def test_cagr(data_ls, index_ls, start, n):
    data = data_ls(start, n)
    index = index_ls(start, n)
    series = Series(data, index=index)
    if data_ls in [int_ls, float_ls, ] and index_ls in [datetime_ls, ]:
        ans = cagr(series)
        assert isinstance(ans, float)
    else:
        with pytest.raises(Exception):
            cagr(series)


@pytest.mark.parametrize('data_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('index_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('start', [10, 100, 1000])
@pytest.mark.parametrize('n', [10, 100, 1000])
def test_mu_sigma(data_ls, index_ls, start, n):
    data = data_ls(start, n)
    index = index_ls(start, n)
    series = Series(data, index=index)
    if data_ls in [int_ls, float_ls, ] and index_ls in [datetime_ls, ]:
        af = detect_annualize_factor(series)
        mu, sigma = mu_sigma(series, af)
        assert isinstance(mu, float)
        assert isinstance(sigma, float)
    else:
        with pytest.raises(Exception):
            mu_sigma(series, detect_annualize_factor(series))


@pytest.mark.parametrize('data_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('index_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('start', [10, 100, 1000])
@pytest.mark.parametrize('n', [10, 100, 1000])
@pytest.mark.parametrize('risk_free', [0, 0.01, 0.05])
def test_sharpe(data_ls, index_ls, start, n, risk_free):
    data = data_ls(start, n)
    index = index_ls(start, n)
    series = Series(data, index=index)
    if data_ls in [int_ls, float_ls, ] and index_ls in [datetime_ls, ]:
        af = detect_annualize_factor(series)
        ans = sharpe(series, af, risk_free)
        assert isinstance(ans, float)
    else:
        with pytest.raises(Exception):
            sharpe(series, detect_annualize_factor(series), risk_free)


@pytest.mark.parametrize('data_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('index_ls', LS_COLLECTIONS)
@pytest.mark.parametrize('start', [10, 100, 1000])
@pytest.mark.parametrize('n', [10, 100, 1000])
def test_drawdown(data_ls, index_ls, start, n):
    data = data_ls(start, n)
    index = index_ls(start, n)
    series = Series(data, index=index)
    if data_ls in [int_ls, float_ls, ] and index_ls in [datetime_ls, ]:
        ddr = drawdown(series)
        assert isinstance(ddr, DrawdownResult)
        assert isinstance(ddr.maxdrawdown, float)
        assert isinstance(ddr.points, DrawdownPoints)
        assert isinstance(ddr.points.start, Timestamp)
        assert isinstance(ddr.points.end, Timestamp)
        assert isinstance(ddr.points.low, float)
        assert isinstance(ddr.points.high, float)
        assert isinstance(ddr.bars, int)
        assert isinstance(ddr.duration, Timedelta)
        assert ddr.points.start <= ddr.points.end
        assert ddr.points.low <= ddr.points.high
        assert ddr.bars >= 0
        assert ddr.duration.days >= 0
    else:
        with pytest.raises(Exception):
            drawdown(series)


def test_calmar():
    assert False
