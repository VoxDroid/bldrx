import hashlib
import json
from pathlib import Path

from bldrx.engine import Engine


def _sha256_hex(path: Path):
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def test_verify_manifest_ok(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "prov"
    t.mkdir(parents=True)
    (t / "file.txt").write_text("content\n")
    manifest = {"files": {"file.txt": _sha256_hex(t / "file.txt")}}
    (t / "bldrx-manifest.json").write_text(json.dumps(manifest))

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    res = engine.verify_template("prov")
    assert res["ok"] is True
    assert res["mismatches"] == []


def test_verify_manifest_mismatch(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "prov"
    t.mkdir(parents=True)
    (t / "file.txt").write_text("content\n")
    manifest = {"files": {"file.txt": "deadbeef"}}
    (t / "bldrx-manifest.json").write_text(json.dumps(manifest))

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    res = engine.verify_template("prov")
    assert res["ok"] is False
    assert "file.txt" in res["mismatches"]


def test_apply_fails_when_verify_true_and_bad_manifest(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "prov"
    t.mkdir(parents=True)
    (t / "file.txt.j2").write_text("Hello {{ project_name }}\n")
    manifest = {"files": {"file.txt.j2": "deadbeef"}}
    (t / "bldrx-manifest.json").write_text(json.dumps(manifest))

    dest = tmp_path / "project"
    dest.mkdir()

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    import pytest

    with pytest.raises(RuntimeError):
        list(
            engine.apply_template(
                "prov", dest, {"project_name": "X"}, force=True, verify=True
            )
        )


def test_verify_manifest_hmac_ok(tmp_path, monkeypatch):
    templates = tmp_path / "templates"
    t = templates / "provh"
    t.mkdir(parents=True)
    (t / "file.txt").write_text("content\n")
    manifest_files = {"file.txt": _sha256_hex(t / "file.txt")}
    import hashlib
    import hmac
    import json

    key = "s3cr3t"
    canonical = json.dumps(
        {"files": manifest_files}, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    h = hmac.new(key.encode("utf-8"), canonical, hashlib.sha256).hexdigest()
    manifest = {"files": manifest_files, "hmac": h}
    (t / "bldrx-manifest.json").write_text(json.dumps(manifest))

    monkeypatch.setenv("BLDRX_MANIFEST_KEY", key)
    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    res = engine.verify_template("provh")
    assert res["ok"] is True
    assert res["signature_present"] is True
    assert res["signature_valid"] is True


def test_verify_manifest_hmac_fail(tmp_path, monkeypatch):
    templates = tmp_path / "templates"
    t = templates / "provh"
    t.mkdir(parents=True)
    (t / "file.txt").write_text("content\n")
    manifest_files = {"file.txt": _sha256_hex(t / "file.txt")}
    manifest = {"files": manifest_files, "hmac": "deadbeef"}
    (t / "bldrx-manifest.json").write_text(json.dumps(manifest))

    monkeypatch.setenv("BLDRX_MANIFEST_KEY", "s3cr3t")
    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    res = engine.verify_template("provh")
    assert res["ok"] is False
    assert res["signature_present"] is True
    assert res["signature_valid"] is False


def test_apply_fails_when_verify_true_and_bad_signature(tmp_path, monkeypatch):
    templates = tmp_path / "templates"
    t = templates / "provh"
    t.mkdir(parents=True)
    (t / "file.txt.j2").write_text("Hello {{ project_name }}\n")
    manifest_files = {"file.txt.j2": _sha256_hex(t / "file.txt.j2")}
    manifest = {"files": manifest_files, "hmac": "deadbeef"}
    (t / "bldrx-manifest.json").write_text(json.dumps(manifest))

    dest = tmp_path / "project"
    dest.mkdir()

    monkeypatch.setenv("BLDRX_MANIFEST_KEY", "s3cr3t")
    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    import pytest

    with pytest.raises(RuntimeError):
        list(
            engine.apply_template(
                "provh", dest, {"project_name": "X"}, force=True, verify=True
            )
        )
