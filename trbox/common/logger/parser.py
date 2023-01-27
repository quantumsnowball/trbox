from pprint import pformat
from typing import Any, Self
from trbox.common.logger import info
from trbox.common.utils import cln


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
        self._sep = ', '
        self._pad = ''

    def _compile(self, fn) -> str:
        header = self._pad if len(self._prefix) == 0 \
            else f'{self._pad}{self._prefix}{self._pad}'
        footer = self._pad if len(self._suffix) == 0 \
            else f'{self._pad}{self._suffix}{self._pad}'
        return ''.join((
            header,
            self._sep.join(map(fn, self._args)),
            footer,
        ))

    def __str__(self) -> str:
        return self._compile(str)

    def __repr__(self) -> str:
        return self._compile(repr)

    #
    # chained modifier methods
    #
    def by(self, who: Any) -> Self:
        who = who if isinstance(who, str) else cln(who)
        self._prefix = f'{who} : '
        return self

    def tag(self, tags: str) -> Self:
        self._suffix = f'#{tags}'
        return self

    def sep(self, sep: str) -> Self:
        self._sep = sep
        return self

    # high-level modifier
    def sparse(self) -> Self:
        self._sep = '\n'
        self._pad = '\n'
        return self
