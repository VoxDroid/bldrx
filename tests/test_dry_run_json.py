from bldrx.engine import Engine


def test_engine_preview_apply_returns_structure(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "chg"
    t.mkdir(parents=True)
    (t / "file.txt.j2").write_text("Hello {{ project_name }}\n")

    dest = tmp_path / "project"
    dest.mkdir()
    (dest / "file.txt").write_text("Hello OLD\n")

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    preview = engine.preview_apply("chg", dest, {"project_name": "NEW"}, force=True)
    assert isinstance(preview, list)
    entry = next((e for e in preview if e["path"].endswith("file.txt")), None)
    assert entry is not None
    assert entry["action"] == "would-render"
    assert "path" in entry and "action" in entry
