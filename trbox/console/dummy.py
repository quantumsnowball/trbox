from typing_extensions import override

from trbox.common.logger import Log
from trbox.common.logger.parser import Memo
from trbox.common.utils import cln
from trbox.console import Console
from trbox.event import Event
from trbox.event.portfolio import EquityCurveUpdate


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

    # handle events

    def handle_equity_curve_update(self, e: EquityCurveUpdate) -> None:
        # TODO
        # should stream these info to the fronend client using websocket
        Log.info(Memo(cln(e), e=e).by(self))

    @override
    def handle(self, e: Event) -> None:
        if isinstance(e, EquityCurveUpdate):
            self.handle_equity_curve_update(e)
