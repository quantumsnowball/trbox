import pytest
from trbox.common.logger import \
    debug, info, warning, error, critical, exception


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
