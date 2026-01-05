from click.testing import CliRunner

from bldrx import __version__
from bldrx.cli import cli


def test_cli_version_flag():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output
