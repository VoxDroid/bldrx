from bldrx.engine import Engine


def test_install_and_uninstall_user_template(tmp_path):
    # create a sample template in temp
    src = tmp_path / "sample_tpl"
    src.mkdir()
    (src / "file.txt.j2").write_text("hello {{ project_name }}")

    engine = Engine(user_templates_root=tmp_path / "user_templates")
    # install
    dest = engine.install_user_template(src, name="sample", force=False)
    assert dest.exists()
    # list templates should include 'sample'
    assert "sample" in engine.list_templates()
    # uninstall
    engine.uninstall_user_template("sample")
    assert "sample" not in engine.list_templates()


def test_templates_search_order(tmp_path, monkeypatch):
    # package templates root
    pkg = tmp_path / "pkg_templates"
    (pkg / "tpl").mkdir(parents=True)
    (pkg / "tpl" / "a.txt.j2").write_text("pkg {{ project_name }}")
    # user templates root
    user = tmp_path / "user_templates"
    (user / "tpl").mkdir(parents=True)
    (user / "tpl" / "a.txt.j2").write_text("user {{ project_name }}")

    # engine default should use user template first
    engine = Engine(templates_root=pkg, user_templates_root=user)
    dest = tmp_path / "out"
    _res = list(engine.apply_template("tpl", dest, {"project_name": "X"}, force=True))
    assert any("rendered" in r for r in _res)
    assert "user X" in (dest / "a.txt").read_text()

    # override with templates_dir pointing to package -> should use package
    dest2 = tmp_path / "out2"
    _res2 = list(
        engine.apply_template(
            "tpl", dest2, {"project_name": "Y"}, force=True, templates_dir=pkg
        )
    )
    assert "pkg Y" in (dest2 / "a.txt").read_text()


def test_list_templates_includes_user_and_package(tmp_path):
    pkg = tmp_path / "pkg_templates"
    (pkg / "p1").mkdir(parents=True)
    user = tmp_path / "user_templates"
    (user / "u1").mkdir(parents=True)
    engine = Engine(templates_root=pkg, user_templates_root=user)
    info = engine.list_templates_info()
    names = [n for n, s in info]
    assert "p1" in names and "u1" in names


def test_env_var_templates_dir(tmp_path, monkeypatch):
    pkg = tmp_path / "pkg_templates"
    (pkg / "envtpl").mkdir(parents=True)
    (pkg / "envtpl" / "f.j2").write_text("env")
    monkeypatch.setenv("BLDRX_TEMPLATES_DIR", str(pkg))
    engine = Engine()
    assert "envtpl" in engine.list_templates()
