from pathlib import Path

from click.testing import CliRunner

from bldrx.cli import cli

runner = CliRunner()
res = runner.invoke(
    cli,
    [
        "preview-template",
        "chg",
        "--render",
        "--meta",
        "project_name=XE",
        "--diff",
        "--json",
    ],
    env={"BLDRX_TEMPLATES_DIR": str(Path("."))},
)
print("exit_code", res.exit_code)
print("exception", repr(res.exception))
print("output:\n", res.output)
