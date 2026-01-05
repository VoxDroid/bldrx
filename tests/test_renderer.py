from bldrx.renderer import Renderer


def test_renderer_simple(tmp_path):
    tdir = tmp_path / "templates"
    tdir.mkdir()
    (tdir / "hello.j2").write_text("Hello {{name}}", encoding="utf-8")
    r = Renderer(str(tdir))
    out = r.render_text("hello.j2", {"name": "World"})
    assert out == "Hello World"
