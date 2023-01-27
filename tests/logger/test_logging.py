import pytest
from trbox.common.logger import debug, info, warning, error, critical, exception
from trbox.common.logger.parser import Log
from trbox.common.utils import cln, ppf


@pytest.mark.parametrize('obj', [
    1, 1.0, True, 'str',
    Exception(), None, ...,
    [1, 'a', ], (1, 'a', ), {1, 'b'}, {1: 'a', }
])
def test_cln(obj):
    name = cln(obj)
    assert isinstance(name, str)
    info(name)


@pytest.mark.parametrize(
    'log', [debug, info, warning, error, critical, exception])
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


def test_ppf():
    obj = dict(a=1, b=2)
    info(obj)
    info(ppf(obj))
    info(dir(obj))
    # info(ppf(dir(obj)), who=obj)
    # info(Log('something', by=self))


@pytest.mark.parametrize('obj', [
    1, 1.0, True, 'str', str, type,
    Exception(), None, ...,
    [1, 'a', ], (1, 'a', ), {1, 'b'}, {1: 'a', },
    [[1, 2], ['3', '4']] * 5
])
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
