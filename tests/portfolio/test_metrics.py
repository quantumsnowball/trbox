import pytest
from pandas import Series, Timedelta, Timestamp

from trbox.portfolio.metrics import cagr, total_return


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


def test_detect_annualize_factor():
    assert False


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


def test_mu_sigma():
    assert False


def test_sharpe():
    assert False


def test_drawdown():
    assert False


def test_calmar():
    assert False
