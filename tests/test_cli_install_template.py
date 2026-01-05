from click.testing import CliRunner

from bldrx.cli import cli


def test_install_template_interactive(tmp_path, monkeypatch):
    # create source template
    src = tmp_path / "src_tpl"
    src.mkdir()
    (src / "t.txt.j2").write_text("hi {{ project_name }}")
    # set user templates dir to a temp dir via env
    user_dir = tmp_path / "user_templates"
    monkeypatch.setenv("BLDRX_TEMPLATES_DIR", str(user_dir))

    runner = CliRunner()
    result = runner.invoke(cli, ["install-template", str(src)], input="\n")
    assert result.exit_code == 0
    assert (user_dir / "src_tpl").exists()


def test_install_template_overwrite_and_rename(tmp_path, monkeypatch):
    src = tmp_path / "src_tpl"
    src.mkdir()
    (src / "t.txt.j2").write_text("hi")
    user_dir = tmp_path / "user_templates"
    (user_dir / "src_tpl").mkdir(parents=True)
    monkeypatch.setenv("BLDRX_TEMPLATES_DIR", str(user_dir))

    runner = CliRunner()
    # Respond: for overwrite prompt -> 'n', then provide new name 'src_tpl2'
    result = runner.invoke(cli, ["install-template", str(src)], input="\nn\nsrc_tpl2\n")
    assert result.exit_code == 0
    assert (user_dir / "src_tpl2").exists()


def test_install_template_cancel(tmp_path, monkeypatch):
    src = tmp_path / "src_tpl"
    src.mkdir()
    (src / "t.txt.j2").write_text("hi")
    user_dir = tmp_path / "user_templates"
    (user_dir / "src_tpl").mkdir(parents=True)
    monkeypatch.setenv("BLDRX_TEMPLATES_DIR", str(user_dir))

    runner = CliRunner()
    # Respond: for overwrite prompt -> 'n', then blank to cancel
    result = runner.invoke(cli, ["install-template", str(src)], input="\nn\n\n")
    assert result.exit_code != 0
    assert "Aborted." in result.output
