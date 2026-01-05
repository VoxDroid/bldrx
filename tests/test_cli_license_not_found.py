from pathlib import Path

from click.testing import CliRunner

from bldrx.cli import cli


def test_add_templates_license_not_found(tmp_path):
    runner = CliRunner()
    dest = tmp_path / "proj"
    dest.mkdir()
    # use a definitely-nonexistent license id to trigger not-found behavior
    result = runner.invoke(
        cli, ["add-templates", str(dest), "--license", "FAKE-LICENSE"]
    )
    assert result.exit_code != 0
    assert "License 'FAKE-LICENSE' not found" in result.output
    assert "Available licenses:" in result.output


def test_new_license_fuzzy_match(tmp_path):
    runner = CliRunner()
    # run 'bldrx new proj --license Apache --meta author_name=VoxDroid --meta year=2026'
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            [
                "new",
                "proj",
                "--templates",
                "python-cli",
                "--license",
                "Apache",
                "--meta",
                "author_name=VoxDroid",
                "--meta",
                "year=2026",
                "--force",
            ],
        )
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        proj = Path("proj")
        assert proj.exists()
        lic = proj / "LICENSE"
        assert lic.exists()
        assert "VoxDroid" in lic.read_text(encoding="utf-8")
