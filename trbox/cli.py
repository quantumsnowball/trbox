import click

from trbox.backtest.lab import Lab


@click.group()
def trbox() -> None:
    pass


@trbox.command()
def lab() -> None:
    print('TrBox Lab: This will spawn a server, serving the trbox-lab frontend to render the current directory as a backtesting lab.')
    lab = Lab(daemon=True)
    lab.start()
