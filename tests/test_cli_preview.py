from click.testing import CliRunner

from bldrx.cli import cli


def test_list_templates_details(tmp_path, monkeypatch):
    # create a temp templates dir with sample template
    tpl_root = tmp_path / "tpls"
    (tpl_root / "foo").mkdir(parents=True)
    (tpl_root / "foo" / "a.txt.j2").write_text("A")
    (tpl_root / "foo" / ".github").mkdir()

    runner = CliRunner()
    result = runner.invoke(
        cli, ["list-templates", "--templates-dir", str(tpl_root), "--details"]
    )
    assert result.exit_code == 0
    assert "foo" in result.output
    assert "a.txt.j2" in result.output


def test_preview_template_raw_and_render(tmp_path, monkeypatch):
    tpl_root = tmp_path / "tpls"
    (tpl_root / "bar").mkdir(parents=True)
    (tpl_root / "bar" / "hello.txt.j2").write_text("Hello {{ who }}")

    runner = CliRunner()
    # raw
    result = runner.invoke(
        cli,
        [
            "preview-template",
            "bar",
            "--file",
            "hello.txt.j2",
            "--templates-dir",
            str(tpl_root),
        ],
    )
    assert result.exit_code == 0
    assert "Hello {{ who }}" in result.output
    # render
    result2 = runner.invoke(
        cli,
        [
            "preview-template",
            "bar",
            "--file",
            "hello.txt.j2",
            "--render",
            "--meta",
            "who=VoxDroid",
            "--templates-dir",
            str(tpl_root),
        ],
    )
    assert result2.exit_code == 0
    assert "Hello VoxDroid" in result2.output
