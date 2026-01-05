from bldrx import engine, plugins, registry, renderer


def test_docstrings_present():
    # engine has key public docstrings
    assert engine.Engine._find_template_src.__doc__
    assert engine.Engine.list_templates.__doc__
    assert engine.Engine.generate_manifest.__doc__
    assert engine.Engine.apply_template.__doc__
    # renderer
    assert renderer.Renderer.render_text.__doc__
    # plugins
    assert plugins.PluginManager.list_plugins.__doc__
    # registry
    assert registry.Registry.publish.__doc__
    assert registry.Registry.list_entries.__doc__
