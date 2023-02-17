import click

from trbox.backtest.lab import Lab


@click.group()
def trbox() -> None:
    pass


@trbox.command()
@click.option('-p', '--port', default=9000)
def lab(port: int) -> None:
    print('TrBox Lab: This will spawn a server, serving the trbox-lab frontend to render the current directory as a backtesting lab.')
    lab = Lab(port=port)
    lab.start()
