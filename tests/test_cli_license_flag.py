from click.testing import CliRunner

from bldrx.cli import cli


def test_add_templates_with_license_flag(tmp_path):
    runner = CliRunner()
    dest = tmp_path / "proj"
    dest.mkdir()
    # include license via flag; provide metadata to render
    result = runner.invoke(
        cli,
        [
            "add-templates",
            str(dest),
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
    # License file should be created
    lic = dest / "LICENSE"
    assert lic.exists()
    text = lic.read_text(encoding="utf-8")
    assert "VoxDroid" in text or "2026" in text
