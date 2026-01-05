from pathlib import Path


def test_readme_has_important_sections():
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "Quickstart" in readme
    assert "Examples" in readme
    assert "Configuration" in readme
    assert "Contributing" in readme
    assert "PROJECT_OUTLINE.md" in readme
