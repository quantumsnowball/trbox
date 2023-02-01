from typing import Any, Callable, TypeVar

from trbox.common.utils import cln

Self = TypeVar("Self", bound="Log")


class Log:
    """
    This helper class is a string post processing class. It is mainly suppose
    to accept str as first argument. However, if non-str is provided, should
    also try to do a str or repr conversion first.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._args = args
        self._kwargs = kwargs
        self._sep = " "
        self._pad = " "
        self._mar = " "
        self._prefix = ""
        self._suffix = ""

    #
    # make string based on the finaly state of the class
    #
    def _compile(self, fn: Callable[[Any], str]) -> str:
        """
        [mar]H1, H2 :[pad]1[sep]2[sep]x=3[sep]y=4[pad]#t1 #t2[mar]
        """

        def header() -> str:
            return self._prefix + " :" if len(self._prefix) > 0 else ""

        def body() -> str:
            args = self._sep.join(map(fn, self._args))
            kwargs = self._sep.join(
                [f"{k}={fn(v)}" for k, v in self._kwargs.items()])
            return self._sep.join([p for p in [args, kwargs] if len(p) > 0])

        def footer() -> str:
            return self._suffix

        def document(*parts: str) -> str:
            doc = self._pad.join([p for p in parts if len(p) > 0])
            return self._mar + doc + self._mar

        return document(header(), body(), footer())

    def __str__(self) -> str:
        return self._compile(str)

    def __repr__(self) -> str:
        return self._compile(repr)

    #
    # chained modifier methods
    #
    def by(self: Self, *who: Any) -> Self:
        who = tuple(map(lambda w: w if isinstance(w, str) else cln(w), who))
        self._prefix = ", ".join(who)
        return self

    def tag(self: Self, *tags: str) -> Self:
        self._suffix = " ".join([f"#{t}" for t in tags])
        return self

    def sep(self: Self, sep: str) -> Self:
        self._sep = sep
        return self

    # high-level modifier
    def sparse(self: Self) -> Self:
        self._sep = "\n"
        self._pad = "\n"
        self._mar = "\n"
        return self
