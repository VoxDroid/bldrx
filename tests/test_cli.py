from pathlib import Path

from click.testing import CliRunner

from bldrx.cli import cli
from bldrx.engine import Engine


def test_list_templates():
    runner = CliRunner()
    result = runner.invoke(cli, ["list-templates"])
    assert result.exit_code == 0
    assert "python-cli" in result.output


def test_new_dry_run(tmp_path):
    runner = CliRunner()
    proj = tmp_path / "myproj"
    result = runner.invoke(
        cli, ["new", str(proj), "--templates", "python-cli", "--dry-run"]
    )
    assert result.exit_code == 0
    assert "would-render" in result.output or "would-copy" in result.output
    # directory may be created for dry-run, but files should not be written
    assert proj.exists()
    assert not (proj / "README.md").exists()


def test_add_templates_dry_run(tmp_path):
    runner = CliRunner()
    proj = tmp_path / "existing"
    proj.mkdir()
    result = runner.invoke(
        cli, ["add-templates", str(proj), "--templates", "python-cli", "--dry-run"]
    )
    assert result.exit_code == 0
    assert "would-render" in result.output or "would-copy" in result.output
    assert not (proj / "README.md").exists()


def test_remove_template_cli(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    proj = tmp_path / "proj"
    metadata = {"project_name": "proj", "author_name": "T", "email": "t@example.com"}
    list(engine.apply_template("python-cli", proj, metadata, force=True))
    readme = proj / "README.md"
    assert readme.exists()

    runner = CliRunner()
    # use --yes to imply removal (now implies --force)
    result = runner.invoke(cli, ["remove-template", str(proj), "python-cli", "--yes"])
    assert result.exit_code == 0
    assert "removed" in result.output
    assert not readme.exists()


def test_remove_template_cli_dry_run(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    proj = tmp_path / "proj2"
    metadata = {"project_name": "proj2", "author_name": "T", "email": "t@example.com"}
    list(engine.apply_template("python-cli", proj, metadata, force=True))
    readme = proj / "README.md"
    assert readme.exists()

    runner = CliRunner()
    # dry-run should not delete
    result = runner.invoke(
        cli, ["remove-template", str(proj), "python-cli", "--dry-run"]
    )
    assert result.exit_code == 0
    assert "would-remove" in result.output or "skipped" in result.output
    assert readme.exists()


def test_list_templates_json():
    runner = CliRunner()
    result = runner.invoke(cli, ["list-templates", "--json"])
    assert result.exit_code == 0
    import json

    data = json.loads(result.output)
    assert isinstance(data, list)
    assert "python-cli" in data
