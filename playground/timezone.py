import datetime
import time

import pytest
from pandas import Timestamp, date_range, to_datetime

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo


@pytest.mark.playground()
def test_now():
    # utc timestamp now
    now = time.time()
    Log.warning(Memo('time.time() =', now))
    # these can produce correct current utc timestamp
    # - timezone aware
    assert now-1 < Timestamp.now(tz='Asia/Hong_Kong').timestamp() < now+1
    assert now-1 < Timestamp.utcnow().timestamp() < now+1
    # - timezone naive
    assert now-1 < Timestamp.now(
        tz='Asia/Hong_Kong').tz_convert(None).timestamp() < now+1
    assert now-1 < Timestamp.utcnow().tz_convert(None).timestamp() < now+1
    assert now-1 < Timestamp.utcnow().tz_localize(None).timestamp() < now+1
    assert now-1 < datetime.datetime.now().timestamp() < now+1
    # these CANNOT produce correct current utc timestamp
    with pytest.raises(AssertionError):
        assert now-1 < Timestamp.now().timestamp() < now+1


@pytest.mark.playground()
def test_to_datetime():
    # these all convert to utc default
    assert to_datetime('1970-01-01').timestamp() == 0
    assert to_datetime('1970-01-01T00:00:00').timestamp() == 0
    assert to_datetime('1970-01-01T00:00:00.000').timestamp() == 0
    with pytest.raises(AssertionError):
        assert to_datetime('1970-01-01T00:00:00.000+0800').timestamp() == 0


@pytest.mark.playground()
@pytest.mark.parametrize('start,end', [
    ('1970-01-01', '1970-01-02'),
    ('1970-01-01T00:00:00', '1970-01-02T00:00:00'),
    ('1970-01-01T00:00:00.000', '1970-01-02T00:00:00.000'),
])
def test_date_range(start, end):
    # these are all utc object
    rng = date_range(start, end, freq='D')
    assert tuple(map(lambda d: d.timestamp(), rng)) == (0, 86400)
    assert tuple(map(lambda d: d.tz, rng)) == (None, None)
    assert tuple(map(lambda d: d.tzinfo, rng)) == (None, None)


@pytest.mark.playground()
def test_tzinfo():
    # these are naive datetime
    assert datetime.datetime(1970, 1, 1).tzinfo == None
    assert Timestamp.now().tzinfo == None
    assert to_datetime('1970-01-01').tzinfo == None
    assert date_range('1970-01-01', '1970-01-02', freq='D')[-1].tzinfo == None
    # these are tz aware datetime
    assert Timestamp.utcnow().tzinfo != None
    assert to_datetime('1970-01-01').tz_localize('UTC').tzinfo != None
    assert to_datetime(
        '1970-01-01').tz_localize('Asia/Hong_Kong').tzinfo != None
    assert date_range('1970-01-01', '1970-01-02', freq='D',
                      tz='UTC')[-1].tzinfo != None
    assert date_range('1970-01-01', '1970-01-02', freq='D',
                      tz='Asia/Hong_Kong')[-1].tzinfo != None


@pytest.mark.playground()
def test_to_string():
    Log.warning(Timestamp.today().isoformat())
    Log.warning(Timestamp.now().isoformat())
    Log.warning(Timestamp.now(tz='Asia/Hong_Kong').isoformat())
    Log.warning(Timestamp.utcnow().isoformat())
