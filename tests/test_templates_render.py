import json
from pathlib import Path

from bldrx.engine import Engine


def load_metadata(tpl_path: Path):
    md = {}
    md_path = tpl_path / "ci_metadata.json"
    if md_path.exists():
        try:
            md = json.loads(md_path.read_text(encoding="utf-8"))
        except Exception:
            md = {}
    return md


def test_all_templates_render(tmp_path):
    engine = Engine()
    failures = []
    for name in engine.list_templates():
        # use package templates (templates_root) so we render packaged templates
        tpl_path = engine._find_template_src(name)
        md = load_metadata(tpl_path)
        # supplement with minimal defaults to help rendering
        minimal = {"project_name": "x", "author_name": "Test", "year": 2026}
        md = {**md, **minimal}
        # validate syntax/undefined
        res = engine.validate_template(name)
        assert "syntax_errors" in res
        # attempt to render each .j2 file
        for rel, undef in (res.get("undefined_variables") or {}).items():
            # render file; if any variable remains undefined this will raise
            try:
                engine.render_template_file(name, rel, md)
            except Exception as e:
                failures.append((name, rel, str(e)))
    assert not failures, f"Template render failures: {failures}"
