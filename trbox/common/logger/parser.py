from pprint import pformat
from typing import Any, Self
from trbox.common.logger import info


class Log:
    '''
    This helper class is a string post processing class. It is mainly suppose
    to accept str as first argument. However, if non-str is provided, should
    also try to do a str or repr conversion first.
    '''

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
        self._prefix = ''
        self._suffix = ''
        self._sep = ' '
        self._padding = ''

    def _compile(self, fn) -> str:
        return ''.join((
            f'{self._padding}',
            f'{self._prefix}',
            f'{self._sep.join(map(fn, self._args))}',
            f'{self._suffix}',
            f'{self._padding}',
        ))

    def __str__(self) -> str:
        return self._compile(str)

    def __repr__(self) -> str:
        return self._compile(repr)

    #
    # chained modifier methods
    #
    def by(self, who: Any) -> Self:
        self._prefix = f'{who}::'
        return self

    def tag(self, tags: str) -> Self:
        self._suffix = f'#{tags}'
        return self

    def sep(self, sep: str) -> Self:
        self._sep = sep
        return self

    # high-level modifier
    def sparse(self) -> Self:
        self._padding = '\n'
        return self
