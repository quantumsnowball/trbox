import os


def foo():
    """
    docstring here
    """
    os.getenv("")


class Foo:
    attr1 = 0
    attr2 = 1

    def __init__(self):
        x = 2
        pass

    def method(self):
        pass

    @property
    def prop1(self) -> None:
        return self


if __name__ == "__main__":
    print(foo().attr1)
