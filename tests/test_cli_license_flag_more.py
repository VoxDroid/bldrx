from pathlib import Path

from click.testing import CliRunner

from bldrx.cli import cli


def test_new_with_license_flag(tmp_path):
    runner = CliRunner()
    # run 'bldrx new proj --license MIT --meta author_name=VoxDroid --meta year=2026'
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(
            cli,
            [
                "new",
                "proj",
                "--templates",
                "python-cli",
                "--license",
                "MIT",
                "--meta",
                "author_name=VoxDroid",
                "--meta",
                "year=2026",
                "--force",
            ],
        )
        assert result.exit_code == 0
        proj = Path("proj")
        assert proj.exists()
        lic = proj / "LICENSE"
        assert lic.exists()
        assert "VoxDroid" in lic.read_text(encoding="utf-8")
