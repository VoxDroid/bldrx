from pathlib import Path


def test_readme_contains_user_templates_examples():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "BLDRX_TEMPLATES_DIR" in readme
    assert "install-template" in readme
    assert "--templates-dir" in readme
