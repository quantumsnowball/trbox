from typing import Any, Callable, TypeVar
from trbox.common.utils import cln


Self = TypeVar('Self', bound='Log')


class Log:
    '''
    This helper class is a string post processing class. It is mainly suppose
    to accept str as first argument. However, if non-str is provided, should
    also try to do a str or repr conversion first.
    '''

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
        self._sep = ', '
        self._pad = ''
        self._mar = ' '
        self._prefix = ''
        self._suffix = ''

    #
    # make string based on the finaly state of the class
    #
    def _compile(self, fn: Callable[[Any], str]) -> str:
        def add_header(t: str) -> str:
            if len(self._prefix) == 0:
                return t + self._pad
            else:
                return t + f'{self._pad}{self._prefix}{self._pad}'

        def add_body(t: str) -> str:
            args = self._sep.join(map(fn, self._args))
            kwargs = self._sep.join([f'{k}={fn(v)}'
                                     for k, v in self._kwargs.items()])
            if len(args) == 0:
                return t + kwargs
            elif len(kwargs) == 0:
                return t + args
            else:
                return t + f'{args}{self._sep}{kwargs}'

        def add_footer(t: str) -> str:
            if len(self._suffix) == 0:
                return t + self._pad
            else:
                return t + f'{self._pad}{self._suffix}{self._pad}'

        def add_margin_space(t):
            if t[0] != ' ':
                t = f' {t}'
            if t[-1] not in (' ', '\n'):
                t = f'{t} '
            return t

        # add parts in correct order
        t = ''
        t = add_header(t)
        t = add_body(t)
        t = add_footer(t)
        t = add_margin_space(t)
        return t

    def __str__(self) -> str:
        return self._compile(str)

    def __repr__(self) -> str:
        return self._compile(repr)

    #
    # chained modifier methods
    #
    def by(self: Self, *who: Any) -> Self:
        who = tuple(map(
            lambda w: w if isinstance(w, str) else cln(w), who))
        # who = who if isinstance(who, str) else cln(who)
        self._prefix = f'{", ".join(who)} : '
        return self

    def tag(self: Self, *tags: str) -> Self:
        self._suffix = ' '.join([f'#{t}' for t in tags])
        return self

    def sep(self: Self, sep: str) -> Self:
        self._sep = sep
        return self

    # high-level modifier
    def sparse(self: Self) -> Self:
        self._sep = '\n'
        self._pad = '\n'
        return self
