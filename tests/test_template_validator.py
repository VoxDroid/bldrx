from bldrx.engine import Engine


def test_template_syntax_error_detected(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "bad"
    t.mkdir(parents=True)
    # create a template with a Jinja syntax error
    (t / "badfile.j2").write_text("Hello {{ project_name \n")

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    res = engine.validate_template("bad")
    assert "badfile.j2" in res["syntax_errors"]
    assert "unexpected end of template" in res["syntax_errors"]["badfile.j2"].lower()


def test_template_unresolved_variables_warned(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "unres"
    t.mkdir(parents=True)
    (t / "file.j2").write_text("Hello {{ project_name }} and {{ missing_var }}\n")

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    res = engine.validate_template("unres")
    assert "file.j2" in res["undefined_variables"]
    vars = res["undefined_variables"]["file.j2"]
    assert "missing_var" in vars
    # project_name should not be reported as it's commonly provided at render time (but we still detect it)
    assert "project_name" in vars


def test_valid_template_no_errors(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "ok"
    t.mkdir(parents=True)
    (t / "file.j2").write_text("Hello {{ project_name }}\n")

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    res = engine.validate_template("ok")
    assert res["syntax_errors"] == {}
    assert "file.j2" in res["undefined_variables"]
    assert "project_name" in res["undefined_variables"]["file.j2"]
