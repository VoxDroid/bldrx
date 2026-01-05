from bldrx.engine import Engine


def test_merge_append_strategy(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "m"
    t.mkdir(parents=True)
    (t / "append.txt.j2").write_text("APPEND {{ project_name }}\n")

    dest = tmp_path / "project"
    dest.mkdir()
    (dest / "append.txt").write_text("EXISTING\n")

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    list(
        engine.apply_template(
            "m", dest, {"project_name": "X"}, force=False, atomic=True, merge="append"
        )
    )

    final = (dest / "append.txt").read_text()
    assert "EXISTING" in final
    assert "APPEND X" in final


def test_merge_marker_strategy(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "m"
    t.mkdir(parents=True)
    (t / "section.md.j2").write_text("New section: {{ project_name }}\n")

    dest = tmp_path / "project"
    dest.mkdir()
    existing = "Header\n<!-- bldrx:start:section.md -->\nOld blocked text\n<!-- bldrx:end:section.md -->\nFooter\n"
    (dest / "section.md").write_text(existing)

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    list(
        engine.apply_template(
            "m", dest, {"project_name": "Y"}, force=False, atomic=True, merge="marker"
        )
    )

    final = (dest / "section.md").read_text()
    assert "Old blocked text" not in final
    assert "New section: Y" in final
