from click.testing import CliRunner

from bldrx.cli import cli


def test_cli_preview_diff_json(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "chg"
    (t).mkdir(parents=True)
    (t / "file.txt.j2").write_text("Hello {{ project_name }}\n")

    runner = CliRunner()
    # run CLI preview-template with --render --diff --json
    result = runner.invoke(
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
        env={"BLDRX_TEMPLATES_DIR": str(templates)},
    )
    assert result.exit_code == 0
    out = result.output.strip()
    import json

    data = json.loads(out)
    # should be a list with at least one entry
    assert isinstance(data, list)
    assert any(
        d["path"].endswith("file.txt") and d["action"] == "would-render" for d in data
    )
