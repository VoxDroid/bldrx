from bldrx.engine import Engine


def test_preview_diff_shows_unified_diff(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "chg"
    (t).mkdir(parents=True)
    (t / "file.txt.j2").write_text("Hello {{ project_name }}\n")

    dest = tmp_path / "project"
    dest.mkdir()
    (dest / "file.txt").write_text("Hello OLD\n")

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    preview = engine.preview_template("chg", dest, {"project_name": "NEW"}, diff=True)

    # find the preview entry for file.txt
    entry = next((e for e in preview if e["path"].endswith("file.txt")), None)
    assert entry is not None
    assert entry["action"] == "would-render"
    # unified diff should contain -Hello OLD and +Hello NEW
    assert "-Hello OLD" in entry["diff"]
    assert "+Hello NEW" in entry["diff"]
