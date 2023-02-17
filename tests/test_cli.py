from click.testing import CliRunner

from trbox.cli import trbox


def test_commands():
    runner = CliRunner()
    r1 = runner.invoke(trbox)
    assert r1.output.startswith('Usage:')
    r2 = runner.invoke(trbox, ['lab'])
    assert r2.exit_code == 0
