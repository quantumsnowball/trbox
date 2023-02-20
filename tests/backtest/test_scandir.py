from trbox.backtest.lab import (TreeDict, scan_for_py_recursive,
                                scan_for_result_recursive, scan_for_source)
from trbox.backtest.utils import Node
from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import ppf

SAMPLE_LAB_PATH = 'tests/backtest/sample-lab'


def test_scan_for_source():
    node = scan_for_source(Node('', 'folder', None, []),
                           basepath=SAMPLE_LAB_PATH)
    Log.info(Memo(ppf(node)).sparse())

    def check_tree(node: Node) -> None:
        for child in node.children:
            if child.type == 'folder':
                Log.info(Memo(folder=child.name))
                check_tree(child)
            else:
                Log.info(Memo(file=child.name))
                assert child.name.endswith('.py')
        return

    check_tree(node)

    Log.info(Memo(ppf(node.dict)).sparse())
    Log.info(Memo(ppf(node.json)).sparse())


def test_scan_for_py_recursive():
    tree = scan_for_py_recursive(SAMPLE_LAB_PATH)
    Log.info(Memo(ppf(tree)).sparse())

    def check_tree(node: TreeDict) -> None:
        for name, item in node.items():
            if item:
                Log.info(Memo(dir=name))
                check_tree(item)
            else:
                Log.info(Memo(file=name))
                assert name.endswith('.py')
        return

    check_tree(tree)


def test_scan_for_result_recursive():
    tree = scan_for_result_recursive(SAMPLE_LAB_PATH)
    Log.info(Memo(ppf(tree)).sparse())

    def check_tree(node: TreeDict) -> None:
        for name, item in node.items():
            if item:
                Log.info(Memo(dir=name))
                check_tree(item)
            else:
                Log.info(Memo(file=name))
                assert name.startswith('.result')
        return

    check_tree(tree)
