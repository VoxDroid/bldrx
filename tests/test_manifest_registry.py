from bldrx.engine import Engine


def test_generate_manifest_and_verify(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "tmpl"
    t.mkdir(parents=True)
    (t / "a.txt").write_text("hello\n")
    (t / "b.txt").write_text("world\n")

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    manifest = engine.generate_manifest("tmpl", templates_dir=templates, write=True)
    assert "files" in manifest
    mp = t / "bldrx-manifest.json"
    assert mp.exists()
    res = engine.verify_template("tmpl", templates_dir=templates)
    assert res["ok"] is True


def test_generate_manifest_with_signing(tmp_path, monkeypatch):
    templates = tmp_path / "templates"
    t = templates / "tmpl2"
    t.mkdir(parents=True)
    (t / "a.txt").write_text("one\n")
    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    manifest = engine.generate_manifest(
        "tmpl2", templates_dir=templates, write=True, sign=True, key="k123"
    )
    assert "hmac" in manifest
    # verify_template should fail if env key not set
    res = engine.verify_template("tmpl2", templates_dir=templates)
    assert res["ok"] is False
    monkeypatch.setenv("BLDRX_MANIFEST_KEY", "k123")
    res2 = engine.verify_template("tmpl2", templates_dir=templates)
    assert res2["ok"] is True
