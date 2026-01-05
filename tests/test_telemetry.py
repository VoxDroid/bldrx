from bldrx.telemetry import Telemetry


def test_telemetry_disabled_by_default(tmp_path, monkeypatch):
    monkeypatch.delenv("BLDRX_ENABLE_TELEMETRY", raising=False)
    t = Telemetry()
    assert t.enabled is False
    assert t.track_event("test") is False


def test_telemetry_writes_log(tmp_path, monkeypatch):
    # enable telemetry and point logfile to tmp
    monkeypatch.setenv("BLDRX_ENABLE_TELEMETRY", "1")
    logfile = tmp_path / "telemetry.log"
    t = Telemetry(logfile=logfile)
    res = t.track_event("op", {"k": "v"})
    assert res is True
    contents = logfile.read_text(encoding="utf-8")
    assert '"event":"op"' in contents


def test_cli_enable_disable_status(monkeypatch):
    from click.testing import CliRunner

    from bldrx.cli import cli

    runner = CliRunner()
    # ensure disabled
    monkeypatch.delenv("BLDRX_ENABLE_TELEMETRY", raising=False)
    r1 = runner.invoke(cli, ["telemetry", "status"])
    assert '"enabled": false' in r1.output.lower()
    r2 = runner.invoke(cli, ["telemetry", "enable"])
    assert r2.exit_code == 0
    r3 = runner.invoke(cli, ["telemetry", "status"])
    assert '"enabled": true' in r3.output.lower()
    r4 = runner.invoke(cli, ["telemetry", "disable"])
    assert r4.exit_code == 0
    r5 = runner.invoke(cli, ["telemetry", "status"])
    assert '"enabled": false' in r5.output.lower()
