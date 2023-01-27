import pytest
from trbox.common.logger import \
    debug, info, warning, error, critical, exception
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
    foo = Foo()
    log('hello world')
    log('hello %s', 'world')
    log('hello %s', 'world', who=foo)
    log(Foo)
    # these should print traceback
    try:
        {'a': 1}['b']
    except Exception as e:
        log(e)

    try:
        print(1 / 0)
    except Exception as e:
        log(e, who=e)


def test_ppf():
    obj = dict(a=1, b=2)
    info(obj)
    info(ppf(obj))
    info(dir(obj))
    info(ppf(dir(obj)), who=obj)
