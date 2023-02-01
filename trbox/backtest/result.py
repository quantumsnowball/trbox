from dataclasses import dataclass

from trbox.common.utils import cln


@dataclass
class Result:
    desc: str = 'A collection of all trader dashboard with summary'

    def __str__(self) -> str:
        return f'{cln(self)}({self.desc})'
