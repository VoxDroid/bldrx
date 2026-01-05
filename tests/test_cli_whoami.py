from click.testing import CliRunner

from bldrx.cli import cli


def test_whoami_hidden_and_outputs():
    runner = CliRunner()
    # Hidden flag exists and prints attribution
    result = runner.invoke(cli, ["--whoami"])
    assert result.exit_code == 0
    assert "Developed by VoxDroid" in result.output
    assert "github.com/VoxDroid" in result.output

    # Ensure --whoami is not listed in help output
    help_out = runner.invoke(cli, ["--help"]).output
    assert "--whoami" not in help_out
