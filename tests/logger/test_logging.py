import pytest
from trbox.common.logger import debug, info, warning, error, critical, exception
from trbox.common.logger.parser import Log
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
    debug, info, warning, error, critical, exception
)


@pytest.mark.parametrize('obj', BASIC + BASIC_COLLECTIONS)
def test_cln(obj):
    name = cln(obj)
    assert isinstance(name, str)
    info(name)


@pytest.mark.parametrize('log', LOG_FUNCTIONS)
def test_logging_function(log):
    class Foo:
        ...
    # foo = Foo()
    log('hello world')
    log('hello %s', 'world')
    # log('hello %s', 'world', who=foo)
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
    info(Log(ppf(obj)).by('test_ppf()'))


@pytest.mark.parametrize('obj', BASIC + BASIC_COLLECTIONS)
def test_parser(obj):
    class Base:
        ...
    base = Base()

    class Foo(Base):
        ...
    foo = Foo()

    info(Log('Case1> Most basic oneliner'))
    info(Log('Normally I am just oneliner',
             a=999)
         .by('Case2', Base))
    info(Log('comment', 1, 'comment2',
             handle=Exception('nothing'))
         .by('Case3', base))
    info(Log('my objects', obj, 2, 3, 4,
             last=10) .sep('||')
         .by('Case4', foo)
         .tag('oneline', 'only'))
    info(Log(obj, 5, 6, 7,
             extra=obj)
         .by('Case5', 'God')
         .tag('alert', 'warning').sparse())
    info(Log(obj, 8, 9, 10,
             age=5, height=10, money=999
             ).sparse()
         .by('Foo')
         .tag('foo', 'bar', 'haha'))
