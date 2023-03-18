from typing import Generic, Protocol, TypeVar


class Animal:
    pass


class Dog(Animal):
    pass


# S = TypeVar('S', bound=Animal, covariant=True)
S = TypeVar('S', bound=Animal, contravariant=True)


class House(Generic[S]):
    ...


T = TypeVar('T', bound=Animal, covariant=True)
# T = TypeVar('T', bound=Animal, contravariant=True)


class Build(Protocol[T]):
    def __call__(self, house: House[T]) -> None:
        ...


def make_it_run(run: Build[Animal]) -> None:
    pass


make_it_run(
