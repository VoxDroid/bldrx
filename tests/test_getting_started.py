from click.testing import CliRunner

from bldrx.cli import cli


def test_getting_started_scaffold_and_preview(tmp_path):
    runner = CliRunner()
    proj = tmp_path / "demo-project"

    # Dry-run first
    r1 = runner.invoke(
        cli,
        [
            "new",
            str(proj),
            "--type",
            "python-cli",
            "--templates",
            "python-cli",
            "--author",
            "Test",
            "--email",
            "test@example.com",
            "--dry-run",
        ],
    )
    assert r1.exit_code == 0
    assert "would-render" in r1.output or "would-copy" in r1.output

    # Now create for real — remove the directory left by dry-run if present
    if proj.exists():
        import shutil

        shutil.rmtree(proj)

    r2 = runner.invoke(
        cli,
        [
            "new",
            str(proj),
            "--type",
            "python-cli",
            "--templates",
            "python-cli",
            "--author",
            "Test",
            "--email",
            "test@example.com",
        ],
    )
    assert r2.exit_code == 0
    # check a few expected files
    assert (proj / "README.md").exists()
    assert (proj / "LICENSE").exists()

    # Preview a single template file rendered
    r3 = runner.invoke(
        cli,
        [
            "preview-template",
            "python-cli",
            "--file",
            "README.md.j2",
            "--render",
            "--meta",
            "project_name=demo",
        ],
    )
    assert r3.exit_code == 0
    assert "demo" in r3.output


def test_getting_started_add_templates_into_existing(tmp_path):
    runner = CliRunner()
    proj = tmp_path / "existing"
    proj.mkdir()

    # Preview inject
    r1 = runner.invoke(
        cli, ["add-templates", str(proj), "--templates", "python-cli", "--dry-run"]
    )
    assert r1.exit_code == 0
    assert "would-render" in r1.output or "would-copy" in r1.output

    # Apply template
    r2 = runner.invoke(
        cli,
        [
            "add-templates",
            str(proj),
            "--templates",
            "python-cli",
            "--author",
            "T",
            "--email",
            "t@example.com",
            "--force",
        ],
    )
    assert r2.exit_code == 0
    assert (proj / "README.md").exists()
