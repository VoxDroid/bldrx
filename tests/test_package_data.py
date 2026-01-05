from bldrx.engine import Engine


def test_templates_root_exists():
    engine = Engine()
    assert (
        engine.templates_root.exists() and engine.templates_root.is_dir()
    ), "Templates directory missing in package"
