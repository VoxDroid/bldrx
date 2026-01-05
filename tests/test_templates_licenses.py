from bldrx.engine import Engine


def test_license_templates_render_and_placeholders():
    engine = Engine()
    # Ensure license templates exist and render with placeholders
    license_templates = [
        t
        for t in engine.list_templates()
        if t.startswith("licenses") or t == "licenses"
    ]
    assert license_templates, "No license templates found in package templates"
    # our license templates are in 'licenses' folder as subfolders; find sub-templates by listing folder
    base = engine.package_templates_root / "licenses"
    assert base.exists()
    for child in base.iterdir():
        if not child.is_dir():
            continue
        tplname = f"licenses/{child.name}"
        # render LICENSE.j2 using metadata
        rendered = engine.render_template_file(
            tplname, "LICENSE.j2", {"author_name": "VoxDroid", "year": 2026}
        )
        assert (
            "VoxDroid" in rendered
            or "2026" in rendered
            or child.name.lower() in rendered.lower()
        )
