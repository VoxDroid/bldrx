from bldrx.engine import Engine


def test_metadata_passed_to_renderer(tmp_path):
    # Create a temporary templates root with a template that references github_username
    templates_root = tmp_path / "templates"
    tdir = templates_root / "custom"
    tdir.mkdir(parents=True)
    tmpl = tdir / "whoami.txt.j2"
    tmpl.write_text("user: {{ github_username }}\nproject: {{ project_name }}")

    engine = Engine(templates_root=templates_root)
    dest = tmp_path / "out"
    metadata = {"project_name": "myproj", "github_username": "tester"}
    _results = list(engine.apply_template("custom", dest, metadata, force=True))
    assert any(r[1] == "rendered" for r in _results)
    out = (dest / "whoami.txt").read_text()
    assert "tester" in out
    assert "myproj" in out
