from bldrx.engine import Engine


def test_wrap_install_preserves_top_level(tmp_path):
    src = tmp_path / ".github"
    (src / "ISSUE_TEMPLATE").mkdir(parents=True)
    (src / "ISSUE_TEMPLATE" / "bug.md.j2").write_text(
        "Bug report for {{ project_name }}"
    )
    user_dir = tmp_path / "user_templates"
    engine = Engine(user_templates_root=user_dir)
    _dest = engine.install_user_template(src, name="ghwrap", force=True, wrap=True)
    # dest should be user_dir/ghwrap/.github/ISSUE_TEMPLATE/bug.md.j2
    assert (user_dir / "ghwrap" / ".github" / "ISSUE_TEMPLATE" / "bug.md.j2").exists()

    # applying template should result in .github present in output
    out = tmp_path / "out"
    list(engine.apply_template("ghwrap", out, {"project_name": "X"}, force=True))
    assert (out / ".github" / "ISSUE_TEMPLATE" / "bug.md").exists()


def test_content_install_copies_contents(tmp_path):
    src = tmp_path / ".github"
    (src / "ISSUE_TEMPLATE").mkdir(parents=True)
    (src / "ISSUE_TEMPLATE" / "bug.md.j2").write_text(
        "Bug report for {{ project_name }}"
    )
    user_dir = tmp_path / "user_templates"
    engine = Engine(user_templates_root=user_dir)
    _dest = engine.install_user_template(src, name="ghcontent", force=True, wrap=False)
    # dest should contain ISSUE_TEMPLATE directly
    assert (user_dir / "ghcontent" / "ISSUE_TEMPLATE" / "bug.md.j2").exists()

    out = tmp_path / "out2"
    list(engine.apply_template("ghcontent", out, {"project_name": "Y"}, force=True))
    # since the top-level .github was not preserved, ISSUE_TEMPLATE should be at root
    assert (out / "ISSUE_TEMPLATE" / "bug.md").exists()
