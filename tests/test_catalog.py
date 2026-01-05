from click.testing import CliRunner

from bldrx.cli import cli


def test_catalog_publish_and_search(tmp_path, monkeypatch):
    runner = CliRunner()
    # create a simple template dir
    t = tmp_path / "tmpl"
    t.mkdir()
    (t / "a.txt").write_text("a")
    # ensure registry is isolated to tmp
    monkeypatch.setenv("BLDRX_REGISTRY_DIR", str(tmp_path / "registry"))
    # publish
    res = runner.invoke(
        cli,
        [
            "catalog",
            "publish",
            str(t),
            "--name",
            "tm",
            "--version",
            "1.2.3",
            "--description",
            "A test",
            "--tags",
            "test,example",
        ],
    )
    assert res.exit_code == 0
    # search
    res2 = runner.invoke(cli, ["catalog", "search", "test"])
    assert "tm" in res2.output
    # info
    res3 = runner.invoke(cli, ["catalog", "info", "tm"])
    assert "1.2.3" in res3.output
    # remove
    res4 = runner.invoke(cli, ["catalog", "remove", "tm", "--yes"])
    assert res4.exit_code == 0
    res5 = runner.invoke(cli, ["catalog", "search", "test"])
    assert "tm" not in res5.output
