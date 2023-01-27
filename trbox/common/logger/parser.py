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
        self._prefix = ''
        self._suffix = ''

    #
    # make string based on the finaly state of the class
    #
    def _compile(self, fn: Callable[[Any], str]) -> str:
        header = self._pad if len(self._prefix) == 0 \
            else f'{self._pad}{self._prefix}{self._pad}'
        args = self._sep.join(map(fn, self._args))
        kwargs = self._sep.join([f'{k}={fn(v)}'
                                 for k, v in self._kwargs.items()])
        body = (f'{args}'
                f'{self._sep if len(args)>0 and len(kwargs) >0 else ""}'
                f'{kwargs}')
        footer = self._pad if len(self._suffix) == 0 \
            else f'{self._pad}{self._suffix}{self._pad}'
        return (f'{header}'
                f'{body}'
                f'{" " if len(self._pad.strip()) == 0 else ""}'
                f'{footer}')

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
