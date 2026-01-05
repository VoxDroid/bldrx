from click.testing import CliRunner

from bldrx.cli import cli


def test_cli_add_templates_dry_run_json(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "chg"
    t.mkdir(parents=True)
    (t / "file.txt.j2").write_text("Hello {{ project_name }}\n")

    dest = tmp_path / "project"
    dest.mkdir()

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "add-templates",
            str(dest),
            "--templates",
            "chg",
            "--dry-run",
            "--json",
            "--meta",
            "project_name=Z",
        ],
        env={"BLDRX_TEMPLATES_DIR": str(templates)},
    )
    assert result.exit_code == 0
    import json

    data = json.loads(result.output.strip().splitlines()[-1])
    # should be a list with our file entry
    assert isinstance(data, list)
    assert any(
        d["path"].endswith("file.txt") and d["action"] == "would-render" for d in data
    )
