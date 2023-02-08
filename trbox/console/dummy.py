from typing_extensions import override

from trbox.console import Console
from trbox.event import Event


class DummyConsole(Console):
    '''
    Default placeholder if no console specificed by user
    '''

    @override
    def start(self) -> None:
        pass

    @override
    def stop(self) -> None:
        pass

    @override
    def handle(self, _: Event) -> None:
        pass
