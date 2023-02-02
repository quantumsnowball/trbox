import pytest

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln, ppf

BASIC = (
    1,
    1.0,
    True,
    'str',
    str, type,
    Exception(),
    None,
    ...,
)

BASIC_COLLECTIONS = (
    [1, 'a', ],
    (1, 'a', ),
    {1, 'b'},
    {1: 'a', },
    [[1, 2], ['3', '4']] * 2
)

LOG_FUNCTIONS = (
    Log.debug, Log.info, Log.warning, Log.error, Log.critical, Log.exception
)


@pytest.mark.parametrize('obj', BASIC + BASIC_COLLECTIONS)
def test_cln(obj):
    name = cln(obj)
    assert isinstance(name, str)
    Log.info(name)


@pytest.mark.parametrize('log', LOG_FUNCTIONS)
def test_logging_function(log):
    class Foo:
        ...
    # foo = Foo()
    log('hello world')
    log('hello %s', 'world')
    # Memo('hello %s', 'world', who=foo)
    log(Foo)
    # these should print traceback
    try:
        {'a': 1}['b']
    except Exception as e:
        log(e)

    try:
        print(1 / 0)
    except Exception as e:
        # log(e, who=e)
        log(e)


@pytest.mark.parametrize('obj', BASIC + BASIC_COLLECTIONS)
def test_ppf(obj):
    Log.info(Memo(ppf(obj)).by('test_ppf()'))


@pytest.mark.parametrize('obj', BASIC + BASIC_COLLECTIONS)
def test_parser_input_types(obj):
    class Base:
        ...
    base = Base()

    class Foo(Base):
        ...
    foo = Foo()

    Log.info(Memo('Case1> Most basic oneliner'))
    Log.info(Memo('Normally I am just oneliner',
                  a=999)
             .by('Case2', Base))
    Log.info(Memo('comment', 1, 'comment2',
                  handle=Exception('nothing'))
             .by('Case3', base))
    Log.info(Memo('my objects', obj, 2, 3, 4,
                  last=10) .sep('||')
             .by('Case4', foo)
             .tag('oneline', 'only'))
    Log.info(Memo(obj, 5, 6, 7,
                  extra=obj)
             .by('Case5', 'God')
             .tag('alert', 'warning').sparse())
    Log.info(Memo(obj, 8, 9, 10,
                  age=5, height=10, money=999
                  ).sparse()
             .by('Foo')
             .tag('foo', 'bar', 'haha'))


@pytest.mark.parametrize('obj, text', [
    (Memo(1), ' 1 '),
    (Memo(1, 2), ' 1 2 '),
    (Memo('1'), ' 1 '),
    (repr(Memo('1')), " '1' "),
    (Memo('1', 2), ' 1 2 '),
    (Memo('1').sparse(), '\n1\n'),
    (Memo('1', 2).sparse(), '\n1\n2\n'),
    (Memo('1', 2).sep('\n'), ' 1\n2 '),
    (Memo('1', x=2), ' 1 x=2 '),
    (Memo('1', x='2'), ' 1 x=2 '),
    (repr(Memo('1', x='2')), " '1' x='2' "),
    (Memo('1', x=2.0, y='3'), ' 1 x=2.0 y=3 '),
    (Memo('1', x=2.0, y=True), ' 1 x=2.0 y=True '),
    (Memo('1', x=2.0, y=True)
     .by('Test'), ' Test : 1 x=2.0 y=True '),
    (Memo('1', x=2.0, y=True)
     .by('Test').tag('test'), ' Test : 1 x=2.0 y=True #test '),
    (Memo('1', x=2.0, y=True)
     .sparse(), '\n1\nx=2.0\ny=True\n'),
    (Memo('1', x=2.0, y=True)
     .by('Test').tag('test')
     .sparse(), '\nTest :\n1\nx=2.0\ny=True\n#test\n'),
])
def test_parser_results(obj, text):
    assert str(obj) == text
