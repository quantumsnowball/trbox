import click

from trbox.backtest.lab import Lab
from trbox.backtest.lab.constants import (DEFAULT_HOST, DEFAULT_PATH,
                                          DEFAULT_PORT)


@click.group()
def trbox() -> None:
    pass


@trbox.command()
@click.argument('path', required=False, type=click.Path(exists=True))
@click.option('-h', '--host', default=DEFAULT_HOST)
@click.option('-p', '--port', default=DEFAULT_PORT)
def lab(path: str, host: str, port: int) -> None:
    # defaults
    if not path:
        path = DEFAULT_PATH
    # lab
    lab = Lab(path, host=host, port=port)
    # asyncio thread
    try:
        lab.start()
        # if I don't join, the asyncio loop can't setup properly
        lab.join()
    except KeyboardInterrupt:
        click.echo('Shtting down Lab ...')
