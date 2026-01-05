from bldrx.engine import Engine


def test_plugin_install_and_load(tmp_path):
    plugins_dir = tmp_path / "plugins"
    engine = Engine(
        user_templates_root=tmp_path / "templates", user_plugins_root=plugins_dir
    )
    # create a simple plugin source file
    src = tmp_path / "p1.py"
    src.write_text(
        '\ndef register(engine):\n    engine.registered_plugins = getattr(engine, "registered_plugins", [])\n    engine.registered_plugins.append("p1")\n'
    )
    # install
    dest = engine.plugin_manager.install_plugin(src, name="p1", force=True)
    assert dest.exists()
    # load plugins and check registration
    engine.plugin_manager.load_plugins()
    assert getattr(engine, "registered_plugins", None) == ["p1"]


def test_cli_plugin_install_list_remove(tmp_path):
    from click.testing import CliRunner

    from bldrx.cli import cli

    plugins_dir = tmp_path / "plugins"
    _engine = Engine(
        user_templates_root=tmp_path / "templates", user_plugins_root=plugins_dir
    )
    src = tmp_path / "p2.py"
    src.write_text(
        '\ndef register(engine):\n    engine.registered_plugins = getattr(engine, "registered_plugins", [])\n    engine.registered_plugins.append("p2")\n'
    )
    runner = CliRunner()
    # install via CLI
    res = runner.invoke(cli, ["plugin", "install", str(src), "--name", "p2"])
    assert res.exit_code == 0
    # list should show p2
    res2 = runner.invoke(cli, ["plugin", "list"])
    assert "p2" in res2.output
    # remove
    res3 = runner.invoke(cli, ["plugin", "remove", "p2", "--yes"])
    assert res3.exit_code == 0
    res4 = runner.invoke(cli, ["plugin", "list"])
    assert "p2" not in res4.output
