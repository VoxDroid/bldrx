import importlib
from datetime import datetime
from pathlib import Path

from bldrx.engine import Engine

engine = Engine()
# Prefer test-provided metadata and targets when available so snapshots match the tests.
try:
    tests_module = importlib.import_module("tests.test_template_snapshots")
    SAMPLE_METADATA = dict(getattr(tests_module, "SAMPLE_METADATA", {}))
    TARGETS = list(getattr(tests_module, "TARGETS", []))
except Exception:
    SAMPLE_METADATA = {
        "project_name": "demo",
        "author_name": "VoxDroid",
        "email": "izeno.contact@gmail.com",
        "github_username": "VoxDroid",
    }
    TARGETS = [
        ("python-cli", "README.md.j2"),
        ("python-cli", "src_main.py.j2"),
        ("github", "CONTRIBUTING.md.j2"),
    ]

# ensure some useful defaults (e.g., funding_url) are present to render support templates
SAMPLE_METADATA.setdefault("funding_url", "https://ko-fi.com/izeno")

for tpl, rel in TARGETS:
    out_dir = Path("tests/snapshots") / tpl
    out_dir.mkdir(parents=True, exist_ok=True)
    rendered = engine.render_template_file(
        tpl, rel, {**SAMPLE_METADATA, "year": datetime.now().year}
    )
    safe = rel.replace("/", "__")
    p = out_dir / (safe + ".snap")
    p.write_text(rendered, encoding="utf-8")
    print("WROTE", p.resolve())
