import click

from trbox.backtest.lab import Lab


@click.group()
def trbox() -> None:
    pass


@trbox.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('-p', '--port', default=9000)
def lab(path: str, port: int) -> None:
    click.echo(f'{path}, {port}')
    lab = Lab(path, port=port, daemon=True)
    lab.start()
