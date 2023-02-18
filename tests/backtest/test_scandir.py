from trbox.backtest.lab import TreeDict, scan_for_st_recursive
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import ppf

SAMPLE_LAB_PATH = 'tests/backtest/sample-lab'


def test_scan_for_st_recursive():
    tree = scan_for_st_recursive(SAMPLE_LAB_PATH)
    Log.info(Memo(ppf(tree)).sparse())

    def check_tree(node: TreeDict) -> None:
        for name, item in node.items():
            if item:
                Log.info(Memo(dir=name))
                check_tree(item)
            else:
                Log.info(Memo(file=name))
                assert name.startswith('st_')
                assert name.endswith('.py')
        return

    check_tree(tree)
