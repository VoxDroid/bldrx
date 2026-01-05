from pathlib import Path

from bldrx.engine import Engine


def test_apply_python_cli(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    dest = tmp_path / "proj"
    metadata = {"project_name": "proj", "author_name": "Test", "email": "t@example.com"}
    _results = list(engine.apply_template("python-cli", dest, metadata, force=True))
    # expecting README, LICENSE, src_main
    assert (dest / "README.md").exists()
    assert (dest / "LICENSE").exists()
    assert any(
        p.suffix == "" or "src_main" in p.name for p in dest.rglob("*")
    )  # basic sanity check for source file presence
    # content check
    readme = dest / "README.md"
    assert "proj" in readme.read_text()


def test_remove_python_cli(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    dest = tmp_path / "proj"
    metadata = {"project_name": "proj", "author_name": "T", "email": "t@example.com"}
    # create files first
    list(engine.apply_template("python-cli", dest, metadata, force=True))
    readme = dest / "README.md"
    assert readme.exists()
    # removing without force should report skipped (safety)
    results = list(engine.remove_template("python-cli", dest, force=False))
    assert any(r[1] in ("skipped", "missing") for r in results)
    # removing with force should remove files
    results2 = list(engine.remove_template("python-cli", dest, force=True))
    assert any(r[1] == "removed" for r in results2)
    assert not readme.exists()


def test_apply_dry_run(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    dest = tmp_path / "proj"
    metadata = {"project_name": "proj", "author_name": "T", "email": "t@example.com"}
    _results = list(
        engine.apply_template("python-cli", dest, metadata, force=False, dry_run=True)
    )
    # Should report would-render or would-copy actions and not create files
    assert any(r[1] in ("would-render", "would-copy") for r in _results)
    assert not (dest / "README.md").exists()


def test_apply_force_behavior(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    dest = tmp_path / "proj"
    metadata = {"project_name": "proj", "author_name": "T", "email": "t@example.com"}
    # create files first
    list(engine.apply_template("python-cli", dest, metadata, force=True))
    readme = dest / "README.md"
    assert readme.exists()
    # modify to simulate local changes
    readme.write_text("original", encoding="utf-8")
    _results = list(engine.apply_template("python-cli", dest, metadata, force=False))
    assert any(r[1] == "skipped" for r in _results)
    # with force True, template should be re-rendered
    _results2 = list(engine.apply_template("python-cli", dest, metadata, force=True))
    assert any(r[1] == "rendered" for r in _results2)


def test_remove_template_dry_run(tmp_path):
    engine = Engine(templates_root=Path(__file__).parent.parent / "bldrx" / "templates")
    dest = tmp_path / "proj"
    metadata = {"project_name": "proj", "author_name": "T", "email": "t@example.com"}
    list(engine.apply_template("python-cli", dest, metadata, force=True))
    readme = dest / "README.md"
    assert readme.exists()
    results = list(engine.remove_template("python-cli", dest, force=True, dry_run=True))
    assert any(r[1] == "would-remove" for r in results)
    assert readme.exists()


def test_manifest_generation_and_verify(tmp_path):
    # small sample template directory and manifest verification
    pkg = tmp_path / "pkg_templates"
    tmpl = pkg / "sample"
    tmpl.mkdir(parents=True)
    (tmpl / "README.md.j2").write_text("Hello {{project_name}}", encoding="utf-8")
    (tmpl / "file.txt").write_text("content", encoding="utf-8")

    engine = Engine(templates_root=pkg)
    m = engine.generate_manifest("sample", write=True)
    assert "files" in m
    v = engine.verify_template("sample")
    assert v["ok"] is True


def test_preview_apply_dry_run(tmp_path):
    pkg = tmp_path / "pkg_templates"
    tmpl = pkg / "sample"
    tmpl.mkdir(parents=True)
    (tmpl / "README.md.j2").write_text("Hello {{project_name}}", encoding="utf-8")

    dest = tmp_path / "dest"
    engine = Engine(templates_root=pkg)
    previews = list(
        engine.apply_template("sample", dest, {"project_name": "X"}, dry_run=True)
    )
    # should include a would-render for README
    assert any(p[1] == "would-render" for p in previews)
