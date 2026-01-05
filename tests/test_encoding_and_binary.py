from bldrx.engine import Engine


def test_skip_non_utf8_jinja_template(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "enc"
    t.mkdir(parents=True)
    # create a template with non-utf8 bytes
    (t / "binary.j2").write_bytes(b"Hello \xff\xff {{ project_name }}\n")

    dest = tmp_path / "project"
    dest.mkdir()

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    actions = list(
        engine.apply_template("enc", dest, {"project_name": "X"}, dry_run=True)
    )
    # should report would-skip-binary for the template file
    assert any(
        "would-skip-binary" in a[1] or "would-skip-binary" in a[1] for a in actions
    )


def test_skip_large_binary_file(tmp_path):
    templates = tmp_path / "templates"
    t = templates / "enc"
    t.mkdir(parents=True)
    # create a large binary file > threshold
    big = t / "big.bin"
    with big.open("wb") as f:
        f.write(b"\x00" * (2_000_000))

    dest = tmp_path / "project"
    dest.mkdir()

    engine = Engine(
        templates_root=templates, user_templates_root=tmp_path / "user_templates"
    )
    actions = list(engine.apply_template("enc", dest, {}, dry_run=True))
    # should report would-skip-large for the binary file
    assert any(
        "would-skip-large" in a[1] or "would-skip-large" in a[1] for a in actions
    )
