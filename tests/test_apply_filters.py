from bldrx.engine import Engine


def _make_template(tmp_path):
    tpl = tmp_path / "tpl"
    tpl.mkdir()
    # raw file
    (tpl / "a.txt").write_text("A")
    (tpl / "b.txt").write_text("B")
    # jinja template
    (tpl / "README.md.j2").write_text("# {{ project_name }}")
    return tmp_path


def test_only_filter(tmp_path):
    pkg = _make_template(tmp_path)
    engine = Engine()
    dest = tmp_path / "out"
    dest.mkdir()
    # only a.txt and README.md
    only = ["a.txt", "README.md"]
    _res = list(
        engine.apply_template(
            "tpl",
            dest,
            {"project_name": "X"},
            force=True,
            templates_dir=str(pkg),
            only_files=only,
        )
    )
    # a.txt and README should be present, b.txt not
    assert (dest / "a.txt").exists()
    assert (dest / "README.md").exists()
    assert not (dest / "b.txt").exists()


def test_except_filter(tmp_path):
    pkg = _make_template(tmp_path)
    engine = Engine()
    dest = tmp_path / "out2"
    dest.mkdir()
    # exclude b.txt
    exclude = ["b.txt"]
    _res = list(
        engine.apply_template(
            "tpl",
            dest,
            {"project_name": "Y"},
            force=True,
            templates_dir=str(pkg),
            except_files=exclude,
        )
    )
    assert (dest / "a.txt").exists()
    assert (dest / "README.md").exists()
    assert not (dest / "b.txt").exists()


def test_only_and_except(tmp_path):
    pkg = _make_template(tmp_path)
    engine = Engine()
    dest = tmp_path / "out3"
    dest.mkdir()
    only = ["a.txt", "b.txt", "README.md"]
    exclude = ["b.txt"]
    _res = list(
        engine.apply_template(
            "tpl",
            dest,
            {"project_name": "Z"},
            force=True,
            templates_dir=str(pkg),
            only_files=only,
            except_files=exclude,
        )
    )
    assert (dest / "a.txt").exists()
    assert (dest / "README.md").exists()
    assert not (dest / "b.txt").exists()
