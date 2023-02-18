from trbox.backtest.lab import scan_for_st_recursive
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import ppf

SAMPLE_LAB_PATH = 'tests/backtest/sample-lab'


def test_scan_for_st_recursive():
    sts = list(scan_for_st_recursive(SAMPLE_LAB_PATH))
    for st in sts:
        assert st.name.startswith('st_')
        assert st.name.endswith('.py')
        assert st.name in st.path
    items = [dict(name=st.name,
                  path=st.path) for st in sts]
    Log.warning(Memo(ppf(items)).sparse())
